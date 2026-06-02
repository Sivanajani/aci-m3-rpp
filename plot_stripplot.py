"""
Statistical Stripplot: CGA vs RDIGA — all individual run values visible.
Mean shown as horizontal bar. Annotated with Mann-Whitney p-value and Cohen's d.
"""

import json
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from scipy import stats


RESULTS_FILE = "results/7seed_200gens_15runs_results.json"
OUTPUT_FILE  = "results/statistical_stripplot.png"

COLORS = {
    "CGA_mut50":   "#4C72B0",
    "CGA_mut80":   "#4C72B0",
    "RDIGA_mut50": "#DD8452",
    "RDIGA_mut80": "#DD8452",
}

ALPHA = 0.05
RNG   = np.random.default_rng(42)


def load_configs(path):
    with open(path, encoding="utf-8") as f:
        data = json.load(f)
    return {entry["config_name"]: entry["all_final_fitness"] for entry in data}


def cohen_d(a, b):
    pooled_std = np.sqrt((np.std(a, ddof=1) ** 2 + np.std(b, ddof=1) ** 2) / 2)
    return (np.mean(a) - np.mean(b)) / pooled_std


def effect_label(d):
    d = abs(d)
    if d < 0.2: return "negligible"
    if d < 0.5: return "small"
    if d < 0.8: return "medium"
    return "large"


def annotate_significance(ax, x1, x2, y_top, p, d):
    y_range = ax.get_ylim()[1] - ax.get_ylim()[0]
    y_line  = y_top + y_range * 0.04
    y_tick  = y_line + y_range * 0.015
    y_text  = y_top + y_range * 0.07

    ax.plot([x1, x1, x2, x2], [y_line, y_tick, y_tick, y_line],
            color="black", linewidth=1.2)

    sig   = "***" if p < 0.001 else ("**" if p < 0.01 else ("*" if p < ALPHA else "n.s."))
    label = f"{sig}  p={p:.4f}\nd={abs(d):.2f} ({effect_label(d)})"
    ax.text((x1 + x2) / 2, y_text, label, ha="center", va="bottom",
            fontsize=8.5, color="black")


def draw_stripplot(ax, groups, title):
    (name_a, data_a), (name_b, data_b) = groups

    for x, data, name in [(1, data_a, name_a), (2, data_b, name_b)]:
        jitter = RNG.uniform(-0.18, 0.18, size=len(data))

        # Individual points
        ax.scatter(x + jitter, data,
                   color=COLORS[name], s=40, alpha=0.75,
                   zorder=3, linewidths=0.5, edgecolors="white")

        # Mean as thick horizontal bar
        mean_val = np.mean(data)
        ax.plot([x - 0.22, x + 0.22], [mean_val, mean_val],
                color=COLORS[name], linewidth=2.5, zorder=4, solid_capstyle="round")

        # Median as dashed line
        median_val = np.median(data)
        ax.plot([x - 0.22, x + 0.22], [median_val, median_val],
                color="white", linewidth=1.5, linestyle="--", zorder=5)

        ax.text(x, ax.get_ylim()[0] - (ax.get_ylim()[1] - ax.get_ylim()[0]) * 0.06,
                f"n={len(data)}", ha="center", va="top", fontsize=8, color="gray")

    ax.set_xticks([1, 2])
    ax.set_xticklabels([name_a, name_b], fontsize=9)
    ax.set_xlim(0.5, 2.5)
    ax.set_title(title, fontsize=10, fontweight="bold", pad=10)
    ax.set_ylabel("Final Fitness", fontsize=9)
    ax.yaxis.grid(True, linestyle="--", alpha=0.4)
    ax.set_axisbelow(True)

    _, p = stats.mannwhitneyu(data_a, data_b, alternative="two-sided")
    d    = cohen_d(data_a, data_b)
    y_max = max(max(data_a), max(data_b))
    annotate_significance(ax, 1, 2, y_max, p, d)


def main():
    configs = load_configs(RESULTS_FILE)

    cga50   = configs["CGA_mut50"]
    cga80   = configs["CGA_mut80"]
    rdiga50 = configs["RDIGA_mut50"]
    rdiga80 = configs["RDIGA_mut80"]

    fig, axes = plt.subplots(2, 2, figsize=(10, 9))
    fig.suptitle("CGA vs RDIGA — Stripplot (each dot = 1 run, bar = mean, dashed = median)",
                 fontsize=11, fontweight="bold", y=1.01)

    draw_stripplot(axes[0][0],
                   [("CGA_mut50", cga50), ("RDIGA_mut50", rdiga50)],
                   "A1) Algorithm Effect  |  μ = 50%")
    draw_stripplot(axes[0][1],
                   [("CGA_mut80", cga80), ("RDIGA_mut80", rdiga80)],
                   "A2) Algorithm Effect  |  μ = 80%")
    draw_stripplot(axes[1][0],
                   [("CGA_mut50", cga50), ("CGA_mut80", cga80)],
                   "B1) Mutation Rate Effect  |  CGA")
    draw_stripplot(axes[1][1],
                   [("RDIGA_mut50", rdiga50), ("RDIGA_mut80", rdiga80)],
                   "B2) Mutation Rate Effect  |  RDIGA")

    legend_handles = [
        mpatches.Patch(color="#4C72B0", alpha=0.85, label="CGA"),
        mpatches.Patch(color="#DD8452", alpha=0.85, label="RDIGA"),
    ]
    fig.legend(handles=legend_handles, loc="lower center", ncol=2,
               fontsize=9, frameon=False, bbox_to_anchor=(0.5, -0.02))

    plt.tight_layout()
    plt.savefig(OUTPUT_FILE, dpi=150, bbox_inches="tight")
    print(f"Saved: {OUTPUT_FILE}")


if __name__ == "__main__":
    main()
