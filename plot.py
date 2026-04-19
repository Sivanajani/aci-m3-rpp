"""
plot.py — Generate all comparison plots from results/results.json.

Usage:
    python plot.py

Outputs (all in results/):
    fitness_curves.png    — avg best fitness per generation, ±1 std band, all 4 configs
    comparison_table.png  — summary table with % improvement column, best row highlighted
    best_paths.png        — best path on the 50×50 grid for each config

Dynamic titles: N_GENERATIONS and N_RUNS are derived from results.json.
                POP_SIZE and CROSSOVER_RATE are imported from experiment.py.
"""

import json
import os
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.colors as mc
import matplotlib.patches as mpatches

RESULTS_DIR = "results"

COLORS = {
    "CGA_mut50"  : "#1f77b4",   # blue
    "CGA_mut80"  : "#ff7f0e",   # orange
    "RDIGA_mut50": "#2ca02c",   # green
    "RDIGA_mut80": "#d62728",   # red
}
LABELS = {
    "CGA_mut50"  : "CGA  μ=50%",
    "CGA_mut80"  : "CGA  μ=80%",
    "RDIGA_mut50": "RDIGA  μ=50%",
    "RDIGA_mut80": "RDIGA  μ=80%",
}


# -----------------------------------------------------------------------
def _load():
    with open(os.path.join(RESULTS_DIR, "results.json")) as fh:
        results = json.load(fh)
    with open(os.path.join(RESULTS_DIR, "best_paths.json")) as fh:
        paths = json.load(fh)
    grid = np.load(os.path.join(RESULTS_DIR, "grid.npy"))
    return results, paths, grid


def _param_str(results):
    """
    Build a compact parameter string for plot titles.
    N_GENERATIONS / N_RUNS are derived from the stored data so the
    string always matches whatever experiment was actually run.
    POP_SIZE / CROSSOVER_RATE are imported from experiment.py.
    """
    n_gens = len(results[0]["avg_fitness_curve"])
    n_runs = len(results[0]["all_final_fitness"])
    try:
        from experiment import POP_SIZE, CROSSOVER_RATE
        pop = POP_SIZE
        xr  = int(round(CROSSOVER_RATE * 100))
    except ImportError:
        pop, xr = "?", "?"
    return (f"Grid: 50×50 | Pop: {pop} | "
            f"Crossover: {xr}% | Gens: {n_gens} | Runs: {n_runs}")


# -----------------------------------------------------------------------
def plot_fitness_curves(results):
    """
    Single plot, all 4 configurations.

    Each curve shows the average best fitness per generation.
    The shaded band is ±1 std_final_fitness (uniform approximation —
    per-generation std is not stored separately in results.json).
    """
    fig, ax = plt.subplots(figsize=(12, 6))

    params = _param_str(results)
    n_gens = len(results[0]["avg_fitness_curve"])

    for r in results:
        name   = r["config_name"]
        color  = COLORS[name]
        curve  = np.array(r["avg_fitness_curve"])
        std    = r["std_final_fitness"]
        gens   = np.arange(1, len(curve) + 1)

        # Main curve
        ax.plot(gens, curve, color=color, linewidth=2.5, label=LABELS[name], zorder=3)

        # ±1 std confidence band (uniform approximation using std_final_fitness)
        ax.fill_between(gens,
                        curve - std,
                        curve + std,
                        color=color, alpha=0.12, zorder=2)

        # Annotate the final value at the right end of the curve
        ax.annotate(
            f"{curve[-1]:.0f}",
            xy=(n_gens, curve[-1]),
            xytext=(n_gens + n_gens * 0.01, curve[-1]),
            fontsize=9, color=color, fontweight="bold",
            va="center",
        )

    # Y-axis: zoom to actual data range
    all_vals = [v for r in results for v in r["avg_fitness_curve"]]
    margin   = (max(all_vals) - min(all_vals)) * 0.08
    ax.set_ylim(min(all_vals) - margin, max(all_vals) + margin)
    ax.set_xlim(1, n_gens * 1.06)

    ax.set_xlabel("Generation", fontsize=12)
    ax.set_ylabel("Avg Best Fitness  (lower = better)", fontsize=12)
    ax.set_title(
        f"Fitness Convergence — CGA vs RDIGA\n{params}",
        fontsize=12, fontweight="bold"
    )
    ax.legend(fontsize=11, loc="upper right")
    ax.grid(True, alpha=0.3)

    # Note about the std band
    fig.text(0.01, 0.01,
             "Shaded band = ±1 std (final-generation std used as uniform approximation)",
             fontsize=7.5, color="grey", style="italic")

    fig.tight_layout()
    out = os.path.join(RESULTS_DIR, "fitness_curves.png")
    fig.savefig(out, dpi=150, bbox_inches="tight")
    plt.close(fig)
    print(f"  Saved: {out}")


# -----------------------------------------------------------------------
def plot_comparison_table(results):
    """
    Summary table with:
      - best row highlighted (bold text + green left border via cell color)
      - % improvement column (relative to the worst-performing config)
    """
    params = _param_str(results)

    worst_fitness  = max(r["avg_final_fitness"] for r in results)
    best_idx       = min(range(len(results)),
                         key=lambda i: results[i]["avg_final_fitness"])

    headers = [
        "Configuration", "Algorithm",
        "Avg Fitness", "± Std",
        "Avg Path Length", "Avg Collisions",
        "Avg Runtime (s)", "Improv. vs Worst",
    ]

    rows = []
    for r in results:
        pct = (worst_fitness - r["avg_final_fitness"]) / worst_fitness * 100
        rows.append([
            LABELS[r["config_name"]],
            r["algorithm"],
            f"{r['avg_final_fitness']:.2f}",
            f"{r['std_final_fitness']:.2f}",
            f"{r['avg_path_length']:.2f}",
            f"{r['avg_obstacle_collisions']:.2f}",
            f"{r['avg_runtime_seconds']:.2f}",
            f"+{pct:.1f}%",
        ])

    fig, ax = plt.subplots(figsize=(14, 3.8))
    ax.axis("off")

    table = ax.table(
        cellText=rows,
        colLabels=headers,
        cellLoc="center",
        loc="center",
    )
    table.auto_set_font_size(False)
    table.set_fontsize(10.5)
    table.scale(1.0, 2.1)

    # Header row — dark blue
    for j in range(len(headers)):
        cell = table[0, j]
        cell.set_facecolor("#2c4f8a")
        cell.set_text_props(color="white", fontweight="bold")

    # Data rows — light config colour; best row gets green tint + bold
    for i, r in enumerate(results):
        row_color = list(mc.to_rgba(COLORS[r["config_name"]]))
        row_color[3] = 0.15

        for j in range(len(headers)):
            cell = table[i + 1, j]
            if i == best_idx:
                # Best row: green tint background, bold text
                cell.set_facecolor("#d4f5d4")
                cell.set_text_props(fontweight="bold")
            else:
                cell.set_facecolor(row_color)

        # Green left-border effect for best row: darken first cell
        if i == best_idx:
            table[i + 1, 0].set_facecolor("#5cb85c")
            table[i + 1, 0].set_text_props(color="white", fontweight="bold")

    ax.set_title(
        f"Experiment Comparison Summary\n{params}",
        fontsize=12, fontweight="bold", pad=16
    )
    fig.tight_layout()
    out = os.path.join(RESULTS_DIR, "comparison_table.png")
    fig.savefig(out, dpi=150, bbox_inches="tight")
    plt.close(fig)
    print(f"  Saved: {out}")


# -----------------------------------------------------------------------
def plot_best_paths(results, paths, grid):
    """
    2×2 grid: best path found per configuration.
    Subplot title: algorithm, mutation rate, avg fitness, collisions, path length.
    Main title: dynamic experiment parameters.
    """
    params = _param_str(results)

    fig, axes = plt.subplots(2, 2, figsize=(14, 14))
    axes = axes.flatten()

    for ax, r in zip(axes, results):
        name  = r["config_name"]
        color = COLORS[name]
        path  = paths[name]

        # Grid image
        img = np.full((*grid.shape, 3), 235, dtype=np.uint8)
        img[grid == 1] = [70, 70, 70]
        img[0,  0 ]    = [0,  180,  0]    # start: green
        img[49, 49]    = [200,  0,  0]    # goal:  red

        ax.imshow(img, origin="upper", interpolation="nearest")

        # Path line
        rows_ = [pt[0] for pt in path]
        cols_ = [pt[1] for pt in path]
        ax.plot(cols_, rows_, color=color, linewidth=2.5, alpha=0.9, zorder=3)
        ax.plot(cols_[0],  rows_[0],  "o", color="lime", markersize=10,
                zorder=4, label="Start (0,0)")
        ax.plot(cols_[-1], rows_[-1], "s", color="red",  markersize=10,
                zorder=4, label="Goal (49,49)")

        # Subplot title: algorithm | mutation rate | key metrics
        mu_pct = int(round(r["mutation_rate"] * 100))
        ax.set_title(
            f"{r['algorithm']}  |  μ = {mu_pct}%\n"
            f"Avg Fitness: {r['avg_final_fitness']:.1f}   "
            f"Collisions: {r['avg_obstacle_collisions']:.1f}   "
            f"Path Length: {r['avg_path_length']:.1f}",
            fontsize=11, fontweight="bold",
            color="white",
            bbox=dict(boxstyle="round,pad=0.4", facecolor=color, alpha=0.88),
        )

        ax.legend(fontsize=9, loc="lower right", framealpha=0.85)
        ax.set_xlabel("Column (0–49)", fontsize=9)
        ax.set_ylabel("Row (0–49)", fontsize=9)
        ax.set_xlim(-1, 50)
        ax.set_ylim(50, -1)
        ax.set_xticks(range(0, 50, 10))
        ax.set_yticks(range(0, 50, 10))
        ax.tick_params(labelsize=8)

    # Shared legend for grid colours
    legend_patches = [
        mpatches.Patch(color="#EBEBEB", label="Free cell"),
        mpatches.Patch(color="#464646", label="Obstacle"),
        mpatches.Patch(color="lime",    label="Start (0,0)"),
        mpatches.Patch(color="red",     label="Goal (49,49)"),
    ]
    fig.legend(handles=legend_patches, loc="lower center",
               ncol=4, fontsize=10, framealpha=0.9,
               bbox_to_anchor=(0.5, -0.01))

    fig.suptitle(
        f"Best Paths — CGA vs RDIGA\n{params}",
        fontsize=13, fontweight="bold", y=1.01
    )
    fig.tight_layout()
    out = os.path.join(RESULTS_DIR, "best_paths.png")
    fig.savefig(out, dpi=150, bbox_inches="tight")
    plt.close(fig)
    print(f"  Saved: {out}")


# -----------------------------------------------------------------------
def main():
    print("Loading results …")
    results, paths, grid = _load()

    print("Generating plots …")
    plot_fitness_curves(results)
    plot_comparison_table(results)
    plot_best_paths(results, paths, grid)

    print("\nAll plots saved to results/")


# -----------------------------------------------------------------------
if __name__ == "__main__":
    main()
