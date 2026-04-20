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
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

# Import our experiment modules from the parent directory
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from grid import Grid
from cga import CGA
from rdiga import RDIGA
from fitness import count_collisions, compute_distance

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
    "results": None,      # list of config result dicts
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

    except Exception as exc:
        state["status"] = "error"
        state["error"]  = str(exc)
        state["log"].append(f"ERROR: {exc}")


# -----------------------------------------------------------------------
@app.post("/run")
def run(params: RunParams):
    if state["status"] == "running":
        raise HTTPException(status_code=409, detail="Experiment already running.")

    # Reset state
    state.update({
        "status" : "running",
        "log"    : [],
        "results": None,
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
    return {
        "status": state["status"],
        "log"   : state["log"],
        "params": state["params"],
    }


@app.get("/results")
def results():
    if state["status"] != "done":
        raise HTTPException(status_code=404, detail="Results not ready yet.")
    return {
        "results": state["results"],
        "paths"  : state["paths"],
        "grid"   : state["grid"],
        "params" : state["params"],
    }
