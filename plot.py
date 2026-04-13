"""
plot.py — Generate all comparison plots from results/results.json.

Usage:
    python plot.py

Outputs (all in results/):
    fitness_curves.png    — avg best fitness per generation for all 4 configs
    comparison_table.png  — summary table with key metrics
    best_paths.png        — best path on the 50×50 grid for each config
"""

import json
import os
import numpy as np
import matplotlib
matplotlib.use("Agg")          # non-interactive backend — no GUI needed
import matplotlib.pyplot as plt

RESULTS_DIR = "results"

# Consistent colour + label per configuration
COLORS = {
    "CGA_mut50"  : "#1f77b4",   # blue
    "CGA_mut80"  : "#ff7f0e",   # orange
    "RDIGA_mut50": "#2ca02c",   # green
    "RDIGA_mut80": "#d62728",   # red
}
LABELS = {
    "CGA_mut50"  : "CGA  μ=50 %",
    "CGA_mut80"  : "CGA  μ=80 %",
    "RDIGA_mut50": "RDIGA  μ=50 %",
    "RDIGA_mut80": "RDIGA  μ=80 %",
}


# -----------------------------------------------------------------------
def _load():
    with open(os.path.join(RESULTS_DIR, "results.json")) as fh:
        results = json.load(fh)
    with open(os.path.join(RESULTS_DIR, "best_paths.json")) as fh:
        paths = json.load(fh)
    grid = np.load(os.path.join(RESULTS_DIR, "grid.npy"))
    return results, paths, grid


# -----------------------------------------------------------------------
def plot_fitness_curves(results):
    """One line per configuration — average best fitness over generations."""
    fig, ax = plt.subplots(figsize=(10, 6))

    for r in results:
        name  = r["config_name"]
        curve = r["avg_fitness_curve"]
        gens  = list(range(1, len(curve) + 1))
        ax.plot(gens, curve,
                color=COLORS[name],
                label=LABELS[name],
                linewidth=2.0)

    ax.set_xlabel("Generation", fontsize=12)
    ax.set_ylabel("Avg Best Fitness  (lower = better)", fontsize=12)
    ax.set_title("Fitness Convergence — CGA vs RDIGA", fontsize=14, fontweight="bold")
    ax.legend(fontsize=11)
    ax.grid(True, alpha=0.35)
    fig.tight_layout()

    out = os.path.join(RESULTS_DIR, "fitness_curves.png")
    fig.savefig(out, dpi=150)
    plt.close(fig)
    print(f"  Saved: {out}")


# -----------------------------------------------------------------------
def plot_comparison_table(results):
    """Render a formatted table image with the key summary statistics."""
    fig, ax = plt.subplots(figsize=(12, 3.2))
    ax.axis("off")

    headers = [
        "Configuration",
        "Avg Fitness",
        "± Std",
        "Avg Path Length",
        "Avg Collisions",
        "Avg Runtime (s)",
    ]
    rows = []
    for r in results:
        rows.append([
            LABELS[r["config_name"]],
            f"{r['avg_final_fitness']:.2f}",
            f"{r['std_final_fitness']:.2f}",
            f"{r['avg_path_length']:.2f}",
            f"{r['avg_obstacle_collisions']:.2f}",
            f"{r['avg_runtime_seconds']:.2f}",
        ])

    table = ax.table(
        cellText=rows,
        colLabels=headers,
        cellLoc="center",
        loc="center",
    )
    table.auto_set_font_size(False)
    table.set_fontsize(11)
    table.scale(1.1, 2.0)

    # Header row styling
    header_color = "#2c4f8a"
    for j in range(len(headers)):
        cell = table[0, j]
        cell.set_facecolor(header_color)
        cell.set_text_props(color="white", fontweight="bold")

    # Data row shading (one colour per config, 20 % opacity)
    config_names = [r["config_name"] for r in results]
    for i, name in enumerate(config_names):
        base = COLORS[name]
        # Convert hex colour to RGBA with alpha = 0.2
        import matplotlib.colors as mc
        rgba = list(mc.to_rgba(base))
        rgba[3] = 0.20
        for j in range(len(headers)):
            table[i + 1, j].set_facecolor(rgba)

    ax.set_title(
        "Experiment Comparison Summary  (avg over 5 runs per config)",
        fontsize=13, fontweight="bold", pad=18
    )
    fig.tight_layout()

    out = os.path.join(RESULTS_DIR, "comparison_table.png")
    fig.savefig(out, dpi=150, bbox_inches="tight")
    plt.close(fig)
    print(f"  Saved: {out}")


# -----------------------------------------------------------------------
def plot_best_paths(results, paths, grid):
    """2×2 grid of subplots — best path on the 50×50 grid per config."""
    fig, axes = plt.subplots(2, 2, figsize=(14, 14))
    axes = axes.flatten()

    for ax, r in zip(axes, results):
        name = r["config_name"]
        path = paths[name]       # list of [row, col] pairs

        # Build an RGB image for the grid
        img = np.full((*grid.shape, 3), 235, dtype=np.uint8)  # light grey (free)
        img[grid == 1] = [70, 70, 70]                         # dark grey (obstacle)
        img[0,  0 ]    = [0,  180,  0]                        # start  — green
        img[49, 49]    = [200,  0,  0]                        # goal   — red

        ax.imshow(img, origin="upper", interpolation="nearest")

        # Draw the path
        rows = [pt[0] for pt in path]
        cols = [pt[1] for pt in path]
        ax.plot(cols, rows,
                color=COLORS[name],
                linewidth=1.8, alpha=0.9,
                label="Path")
        ax.plot(cols[0],  rows[0],  "o",
                color="lime",   markersize=9, label="Start")
        ax.plot(cols[-1], rows[-1], "s",
                color="red",    markersize=9, label="Goal")

        ax.set_title(
            f"{LABELS[name]}\n"
            f"Fitness={r['avg_final_fitness']:.1f}   "
            f"Collisions={r['avg_obstacle_collisions']:.1f}   "
            f"Length={r['avg_path_length']:.1f}",
            fontsize=11
        )
        ax.legend(fontsize=9, loc="upper left")
        ax.set_xlabel("Column")
        ax.set_ylabel("Row")
        ax.set_xlim(-1, 50)
        ax.set_ylim(50, -1)    # row 0 at top

    fig.suptitle(
        "Best Paths on 50×50 Grid  (grey = obstacle, green = start, red = goal)",
        fontsize=14, fontweight="bold"
    )
    fig.tight_layout()

    out = os.path.join(RESULTS_DIR, "best_paths.png")
    fig.savefig(out, dpi=150)
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
