"""
backend/main.py — FastAPI server for the ACI M3 RPP experiment.

Endpoints:
    POST /run        start experiment with given parameters
    GET  /status     poll for progress + completion
    GET  /results    fetch full results when done
"""

import sys
import os
import random
import threading
import numpy as np
from scipy import stats as scipy_stats
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

# Import our experiment modules from the parent directory
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from grid import Grid
from cga import CGA
from rdiga import RDIGA

# -----------------------------------------------------------------------
app = FastAPI(title="ACI M3 — RPP Experiment API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# -----------------------------------------------------------------------
# In-memory state (one experiment at a time)
# -----------------------------------------------------------------------
state = {
    "status" : "idle",    # idle | running | done | error
    "log"    : [],        # list of progress strings
    "results": [],        # list of config result dicts
    "grid"   : None,      # 50×50 list-of-lists (0/1)
    "paths"  : None,      # {config_name: [[r,c], ...]}
    "params" : None,      # last used params
    "error"  : None,
}

CONFIGS = [
    {"name": "CGA_mut50",   "algo": "CGA",   "mutation_rate": 0.50},
    {"name": "CGA_mut80",   "algo": "CGA",   "mutation_rate": 0.80},
    {"name": "RDIGA_mut50", "algo": "RDIGA", "mutation_rate": 0.50},
    {"name": "RDIGA_mut80", "algo": "RDIGA", "mutation_rate": 0.80},
]

POP_SIZE       = 55
CROSSOVER_RATE = 0.50


# -----------------------------------------------------------------------
class RunParams(BaseModel):
    """Parameters for a single experiment run."""

    n_generations: int = 150
    n_runs:        int = 10
    seed:          int = 42


# -----------------------------------------------------------------------
def _run_experiment(params: RunParams):
    """Runs in a background thread. Updates `state` throughout."""
    try:
        np.random.seed(params.seed)
        random.seed(params.seed)

        state["log"].append("Generating 50×50 grid with 25% obstacles …")
        grid = Grid()
        state["log"].append(f"Grid ready — {int(grid.grid.sum())} obstacles placed.\n")

        all_results = []
        paths       = {}

        for cfg_idx, config in enumerate(CONFIGS):
            name = config["name"]
            algo_name = config["algo"]
            mu = config["mutation_rate"]
            state["log"].append(
                f"[{cfg_idx+1}/4]  {name}  (μ={int(mu*100)}%)"
            )

            all_curves     = []
            all_fitness    = []
            all_lengths    = []
            all_collisions = []
            all_runtimes   = []
            best_chrom_overall   = None
            best_fitness_overall = float("inf")

            for run_idx in range(params.n_runs):
                kwargs = dict(
                    pop_size=POP_SIZE,
                    crossover_rate=CROSSOVER_RATE,
                    mutation_rate=mu,
                    n_generations=params.n_generations,
                )
                algo = CGA(**kwargs) if algo_name == "CGA" else RDIGA(**kwargs)
                curve, best_chrom, stats = algo.run(grid)

                all_curves.append(curve)
                all_fitness.append(stats["best_fitness"])
                all_lengths.append(stats["path_length"])
                all_collisions.append(stats["obstacle_collisions"])
                all_runtimes.append(stats["runtime_seconds"])

                if stats["best_fitness"] < best_fitness_overall:
                    best_fitness_overall = stats["best_fitness"]
                    best_chrom_overall   = best_chrom

                state["log"].append(
                    f"  Run {run_idx+1}/{params.n_runs} — "
                    f"fitness={stats['best_fitness']:.1f}  "
                    f"collisions={stats['obstacle_collisions']}  "
                    f"length={stats['path_length']:.1f}  "
                    f"time={stats['runtime_seconds']:.1f}s"
                )

            avg_curve = np.mean(all_curves, axis=0).tolist()
            best_path = [list(pt) for pt in best_chrom_overall.get_full_path()]
            paths[name] = best_path

            result = {
                "config_name"            : name,
                "algorithm"              : algo_name,
                "mutation_rate"          : mu,
                "avg_fitness_curve"      : avg_curve,
                "avg_final_fitness"      : float(np.mean(all_fitness)),
                "std_final_fitness"      : float(np.std(all_fitness)),
                "avg_path_length"        : float(np.mean(all_lengths)),
                "avg_obstacle_collisions": float(np.mean(all_collisions)),
                "avg_runtime_seconds"    : float(np.mean(all_runtimes)),
                "all_final_fitness"      : all_fitness,
            }
            all_results.append(result)
            state["log"].append(
                f"  → Avg fitness: {result['avg_final_fitness']:.2f} "
                f"± {result['std_final_fitness']:.2f}\n"
            )

        state["results"] = all_results
        state["paths"]   = paths
        state["grid"]    = grid.grid.tolist()
        state["status"]  = "done"
        state["log"].append("Experiment complete!")

    except Exception as exc:  # pylint: disable=broad-exception-caught
        state["status"] = "error"
        state["error"]  = str(exc)
        state["log"].append(f"ERROR: {exc}")


# -----------------------------------------------------------------------
@app.post("/run")
def run(params: RunParams):
    """Start the experiment with the given parameters."""
    if state["status"] == "running":
        raise HTTPException(status_code=409, detail="Experiment already running.")

    # Reset state
    state.update({
        "status" : "running",
        "log"    : [],
        "results": [],
        "grid"   : None,
        "paths"  : None,
        "error"  : None,
        "params" : params.dict(),
    })

    thread = threading.Thread(target=_run_experiment, args=(params,), daemon=True)
    thread.start()
    return {"message": "Experiment started."}


@app.get("/status")
def status():
    """Return current experiment status and log."""
    return {
        "status": state["status"],
        "log"   : state["log"],
        "params": state["params"],
    }


@app.get("/results")
def results():
    """Return full results once the experiment is complete."""
    if state["status"] != "done":
        raise HTTPException(status_code=404, detail="Results not ready yet.")
    return {
        "results": state["results"],
        "paths"  : state["paths"],
        "grid"   : state["grid"],
        "params" : state["params"],
    }


@app.get("/statistics")
def statistics():
    """Return boxplot stats and pairwise statistical tests for all configs."""
    if state["status"] != "done":
        raise HTTPException(status_code=404, detail="Results not ready yet.")

    configs = {r["config_name"]: np.array(r["all_final_fitness"]) for r in state["results"]}

    def boxplot_stats(arr):
        q1, med, q3 = np.percentile(arr, [25, 50, 75])
        iqr = q3 - q1
        lower, upper = q1 - 1.5 * iqr, q3 + 1.5 * iqr
        inliers  = arr[(arr >= lower) & (arr <= upper)]
        outliers = arr[(arr < lower)  | (arr > upper)]
        return {
            "q1"      : float(q1),
            "median"  : float(med),
            "q3"      : float(q3),
            "min"     : float(inliers.min()) if len(inliers) else float(arr.min()),
            "max"     : float(inliers.max()) if len(inliers) else float(arr.max()),
            "mean"    : float(arr.mean()),
            "outliers": outliers.tolist(),
        }

    boxplots = {name: boxplot_stats(arr) for name, arr in configs.items()}

    def effect_label(d):
        d = abs(d)
        if d < 0.2:
            return "negligible"
        if d < 0.5:
            return "small"
        if d < 0.8:
            return "medium"
        return "large"

    comparisons = [
        ("CGA_mut50",   "RDIGA_mut50", "Algorithm Effect (μ=50%)"),
        ("CGA_mut80",   "RDIGA_mut80", "Algorithm Effect (μ=80%)"),
        ("CGA_mut50",   "CGA_mut80",   "Mutation Rate Effect (CGA)"),
        ("RDIGA_mut50", "RDIGA_mut80", "Mutation Rate Effect (RDIGA)"),
    ]

    tests = []
    for name_a, name_b, label in comparisons:
        a, b = configs[name_a], configs[name_b]
        mw_stat, mw_p = scipy_stats.mannwhitneyu(a, b, alternative="two-sided")
        n       = len(a) + len(b)
        mu_u    = len(a) * len(b) / 2
        sigma_u = np.sqrt(len(a) * len(b) * (n + 1) / 12)
        z       = float((mw_stat - mu_u) / sigma_u)
        t_stat, t_p = scipy_stats.ttest_ind(a, b, equal_var=False)
        pooled_std  = np.sqrt((np.std(a, ddof=1)**2 + np.std(b, ddof=1)**2) / 2)
        d = float((np.mean(a) - np.mean(b)) / pooled_std)
        tests.append({
            "label"      : label,
            "name_a"     : name_a,
            "name_b"     : name_b,
            "mw_u"       : float(mw_stat),
            "mw_z"       : z,
            "mw_p"       : float(mw_p),
            "t_stat"     : float(t_stat),
            "t_p"        : float(t_p),
            "cohens_d"   : d,
            "effect"     : effect_label(d),
            "significant": bool(mw_p < 0.05),
        })

    return {"boxplots": boxplots, "tests": tests}
