"""
experiment.py — Run all four CGA / RDIGA configurations and save results.

Usage:
    python experiment.py

Configurations:
    1.  CGA   — mutation rate 50 %
    2.  CGA   — mutation rate 80 %
    3.  RDIGA — mutation rate 50 %
    4.  RDIGA — mutation rate 80 %

Each configuration runs N_RUNS = 5 independent times on the SAME grid
(so results are directly comparable).

Outputs:
    results/results.json      — aggregated metrics for all configurations
    results/best_paths.json   — best path waypoints per configuration
    results/grid.npy          — the shared 50×50 obstacle grid
"""

import json
import os
import numpy as np

from grid import Grid
from cga import CGA
from rdiga import RDIGA

# -----------------------------------------------------------------------
# Experiment hyper-parameters (must match the paper exactly)
# -----------------------------------------------------------------------
POP_SIZE        = 55
CROSSOVER_RATE  = 0.50
N_GENERATIONS   = 150
N_RUNS          = 10
RESULTS_DIR     = "results"

CONFIGS = [
    {"name": "CGA_mut50",   "algo": "CGA",   "mutation_rate": 0.50},
    {"name": "CGA_mut80",   "algo": "CGA",   "mutation_rate": 0.80},
    {"name": "RDIGA_mut50", "algo": "RDIGA", "mutation_rate": 0.50},
    {"name": "RDIGA_mut80", "algo": "RDIGA", "mutation_rate": 0.80},
]


# -----------------------------------------------------------------------
def _build_algo(algo_name, mutation_rate):
    """Instantiate CGA or RDIGA with shared hyper-parameters."""
    kwargs = dict(
        pop_size=POP_SIZE,
        crossover_rate=CROSSOVER_RATE,
        mutation_rate=mutation_rate,
        n_generations=N_GENERATIONS,
    )
    return CGA(**kwargs) if algo_name == "CGA" else RDIGA(**kwargs)


# -----------------------------------------------------------------------
def run_config(config, grid):
    """
    Execute N_RUNS independent runs for one configuration.
    Returns a result dict with averaged metrics and the best path found.
    """
    name      = config["name"]
    algo_name = config["algo"]
    mu        = config["mutation_rate"]

    all_curves     = []   # fitness curve per run — shape (N_RUNS, N_GENERATIONS)
    all_fitness    = []
    all_lengths    = []
    all_collisions = []
    all_runtimes   = []

    best_chrom_overall   = None
    best_fitness_overall = float("inf")

    for run_idx in range(N_RUNS):
        print(f"    Run {run_idx + 1}/{N_RUNS} ...", end=" ", flush=True)

        algo = _build_algo(algo_name, mu)
        curve, best_chrom, stats = algo.run(grid)

        all_curves.append(curve)
        all_fitness.append(stats["best_fitness"])
        all_lengths.append(stats["path_length"])
        all_collisions.append(stats["obstacle_collisions"])
        all_runtimes.append(stats["runtime_seconds"])

        if stats["best_fitness"] < best_fitness_overall:
            best_fitness_overall = stats["best_fitness"]
            best_chrom_overall   = best_chrom

        print(
            f"fitness={stats['best_fitness']:.2f}  "
            f"collisions={stats['obstacle_collisions']}  "
            f"length={stats['path_length']:.1f}  "
            f"time={stats['runtime_seconds']:.1f}s"
        )

    avg_curve = np.mean(all_curves, axis=0).tolist()

    # Best path stored as list-of-lists for JSON serialisation
    best_path_serialisable = [list(pt) for pt in best_chrom_overall.get_full_path()]

    return {
        "config_name"           : name,
        "algorithm"             : algo_name,
        "mutation_rate"         : mu,
        # fitness curve (averaged over runs) — one value per generation
        "avg_fitness_curve"     : avg_curve,
        # summary statistics
        "avg_final_fitness"     : float(np.mean(all_fitness)),
        "std_final_fitness"     : float(np.std(all_fitness)),
        "avg_path_length"       : float(np.mean(all_lengths)),
        "avg_obstacle_collisions": float(np.mean(all_collisions)),
        "avg_runtime_seconds"   : float(np.mean(all_runtimes)),
        # per-run raw values (useful for further analysis)
        "all_final_fitness"     : all_fitness,
        # best path found across all runs (for plotting)
        "best_path"             : best_path_serialisable,
    }


# -----------------------------------------------------------------------
def main():
    os.makedirs(RESULTS_DIR, exist_ok=True)

    print("=" * 65)
    print("  RPP Numerical Experiment — CGA vs RDIGA on 50×50 Grid")
    print("=" * 65)
    print(
        f"  Grid: {50}×{50}  |  25 % obstacles  |  "
        f"Pop: {POP_SIZE}  |  Crossover: {CROSSOVER_RATE*100:.0f} %  |  "
        f"Gens: {N_GENERATIONS}  |  Runs/config: {N_RUNS}"
    )
    print()

    # One shared grid for all four configurations
    print("  Generating shared 50×50 grid …")
    grid = Grid()
    n_obs = int(grid.grid.sum())
    print(f"  Grid ready — {n_obs} obstacles placed.\n")

    all_results = []

    for i, config in enumerate(CONFIGS):
        print(
            f"[{i + 1}/4]  {config['name']}"
            f"  (mutation = {config['mutation_rate'] * 100:.0f} %)"
        )
        result = run_config(config, grid)
        all_results.append(result)
        print(
            f"  → Avg final fitness : {result['avg_final_fitness']:.2f} "
            f"± {result['std_final_fitness']:.2f}\n"
        )

    # ---- Save results.json (without best_path — kept in best_paths.json) ----
    metrics_only = [
        {k: v for k, v in r.items() if k != "best_path"}
        for r in all_results
    ]
    json_path = os.path.join(RESULTS_DIR, "results.json")
    with open(json_path, "w") as fh:
        json.dump(metrics_only, fh, indent=2)
    print(f"  Metrics saved  →  {json_path}")

    # ---- Save best_paths.json ------------------------------------------------
    paths_data = {r["config_name"]: r["best_path"] for r in all_results}
    paths_path = os.path.join(RESULTS_DIR, "best_paths.json")
    with open(paths_path, "w") as fh:
        json.dump(paths_data, fh)
    print(f"  Best paths saved →  {paths_path}")

    # ---- Save grid.npy (needed by plot.py) -----------------------------------
    grid_path = os.path.join(RESULTS_DIR, "grid.npy")
    np.save(grid_path, grid.grid)
    print(f"  Grid saved       →  {grid_path}")

    print()
    print("  All done!  Run:  python plot.py")
    print("=" * 65)


# -----------------------------------------------------------------------
if __name__ == "__main__":
    main()
