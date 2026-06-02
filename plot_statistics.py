"""
Statistical Boxplots: CGA vs RDIGA — Fitness Comparison
Annotated with Mann-Whitney p-value and Cohen's d effect size.
"""

import json
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from scipy import stats


RESULTS_FILE = "results/7seed_200gens_15runs_results.json"
OUTPUT_FILE  = "results/statistical_boxplots.png"

COLORS = {
    "CGA_mut50":   "#4C72B0",
    "CGA_mut80":   "#4C72B0",
    "RDIGA_mut50": "#DD8452",
    "RDIGA_mut80": "#DD8452",
}

ALPHA = 0.05


def load_configs(path):
    with open(path) as f:
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
    """Draw significance bracket with p-value and Cohen's d above two boxes."""
    y_range = ax.get_ylim()[1] - ax.get_ylim()[0]
    y_line = y_top + y_range * 0.04
    y_text = y_top + y_range * 0.07

    y_tick = y_line + y_range * 0.015
    ax.plot([x1, x1, x2, x2], [y_line, y_tick, y_tick, y_line],
            color="black", linewidth=1.2)

    sig = "***" if p < 0.001 else ("**" if p < 0.01 else ("*" if p < ALPHA else "n.s."))
    label = f"{sig}  p={p:.4f}\nd={abs(d):.2f} ({effect_label(d)})"
    ax.text((x1 + x2) / 2, y_text, label, ha="center", va="bottom",
            fontsize=8.5, color="black")


def draw_boxplot(ax, groups, title):
    """Draw a single subplot with two boxplots and annotation."""
    (name_a, data_a), (name_b, data_b) = groups

    bp = ax.boxplot(
        [data_a, data_b],
        patch_artist=True,
        widths=0.45,
        medianprops=dict(color="white", linewidth=2),
        whiskerprops=dict(linewidth=1.2),
        capprops=dict(linewidth=1.2),
        flierprops=dict(marker="o", markersize=4, linestyle="none",
                        markerfacecolor="gray", alpha=0.6),
    )

    bp["boxes"][0].set_facecolor(COLORS[name_a])
    bp["boxes"][1].set_facecolor(COLORS[name_b])
    bp["boxes"][0].set_alpha(0.4)
    bp["boxes"][1].set_alpha(0.4)

    # Stripplot: jittered individual data points overlaid on each box
    rng = np.random.default_rng(42)
    for x, data, name in [(1, data_a, name_a), (2, data_b, name_b)]:
        jitter = rng.uniform(-0.12, 0.12, size=len(data))
        ax.scatter(x + jitter, data, color=COLORS[name],
                   s=28, alpha=0.85, zorder=3, linewidths=0.4,
                   edgecolors="white")

    ax.set_xticks([1, 2])
    ax.set_xticklabels([name_a, name_b], fontsize=9)
    ax.set_title(title, fontsize=10, fontweight="bold", pad=10)
    ax.set_ylabel("Final Fitness", fontsize=9)
    ax.yaxis.grid(True, linestyle="--", alpha=0.5)
    ax.set_axisbelow(True)

    _, p = stats.mannwhitneyu(data_a, data_b, alternative="two-sided")
    d = cohen_d(data_a, data_b)

    y_max = max(max(data_a), max(data_b))
    annotate_significance(ax, 1, 2, y_max, p, d)

    # Add n= label below each box
    for x, data in [(1, data_a), (2, data_b)]:
        ax.text(x, ax.get_ylim()[0] - (ax.get_ylim()[1] - ax.get_ylim()[0]) * 0.06,
                f"n={len(data)}", ha="center", va="top", fontsize=8, color="gray")


def main():
    configs = load_configs(RESULTS_FILE)

    cga50   = configs["CGA_mut50"]
    cga80   = configs["CGA_mut80"]
    rdiga50 = configs["RDIGA_mut50"]
    rdiga80 = configs["RDIGA_mut80"]

    fig, axes = plt.subplots(2, 2, figsize=(10, 9))
    fig.suptitle("CGA vs RDIGA — Statistical Comparison (Mann-Whitney U)",
                 fontsize=13, fontweight="bold", y=1.01)

    # Row A: Algorithm effect
    draw_boxplot(axes[0][0],
                 [("CGA_mut50", cga50), ("RDIGA_mut50", rdiga50)],
                 "A1) Algorithm Effect  |  μ = 50%")
    draw_boxplot(axes[0][1],
                 [("CGA_mut80", cga80), ("RDIGA_mut80", rdiga80)],
                 "A2) Algorithm Effect  |  μ = 80%")

    # Row B: Mutation rate effect
    draw_boxplot(axes[1][0],
                 [("CGA_mut50", cga50), ("CGA_mut80", cga80)],
                 "B1) Mutation Rate Effect  |  CGA")
    draw_boxplot(axes[1][1],
                 [("RDIGA_mut50", rdiga50), ("RDIGA_mut80", rdiga80)],
                 "B2) Mutation Rate Effect  |  RDIGA")

    # Legend
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
