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
OUTPUT_FILE  = "results/200_statistical_boxplots.png"

COLORS = {
    "CGA_mut50":   "#2166AC",
    "CGA_mut80":   "#2166AC",
    "RDIGA_mut50": "#D6604D",
    "RDIGA_mut80": "#D6604D",
}

ALPHA = 0.05

plt.rcParams.update({
    "font.family":       "sans-serif",
    "font.size":         10,
    "axes.titlesize":    10,
    "axes.titleweight":  "bold",
    "axes.labelsize":    9,
    "xtick.labelsize":   8.5,
    "ytick.labelsize":   8.5,
    "axes.spines.top":   False,
    "axes.spines.right": False,
    "axes.grid":         True,
    "grid.linestyle":    "--",
    "grid.alpha":        0.4,
})


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


def draw_boxplot(ax, groups, title):
    (name_a, data_a), (name_b, data_b) = groups

    all_vals = list(data_a) + list(data_b)
    y_min = min(all_vals)
    y_max = max(all_vals)
    y_range = y_max - y_min

    # Reserve headroom for annotation bracket
    ax.set_ylim(y_min - y_range * 0.08, y_max + y_range * 0.30)

    bp = ax.boxplot(
        [data_a, data_b],
        patch_artist=True,
        widths=0.42,
        medianprops={"color": "white", "linewidth": 2},
        whiskerprops={"linewidth": 1.2},
        capprops={"linewidth": 1.2},
        flierprops={"marker": "o", "markersize": 3.5,
                    "linestyle": "none", "markerfacecolor": "gray",
                    "alpha": 0.5},
    )

    bp["boxes"][0].set_facecolor(COLORS[name_a])
    bp["boxes"][1].set_facecolor(COLORS[name_b])
    bp["boxes"][0].set_alpha(0.45)
    bp["boxes"][1].set_alpha(0.45)

    # Jittered individual points overlaid on boxes
    rng = np.random.default_rng(42)
    for x, data, name in [(1, data_a, name_a), (2, data_b, name_b)]:
        jitter = rng.uniform(-0.12, 0.12, size=len(data))
        ax.scatter(x + jitter, data, color=COLORS[name],
                   s=26, alpha=0.80, zorder=3,
                   linewidths=0.4, edgecolors="white")

    # Significance annotation
    _, p = stats.mannwhitneyu(data_a, data_b, alternative="two-sided")
    d = cohen_d(data_a, data_b)

    y_bracket = y_max + y_range * 0.10
    y_tick    = y_bracket + y_range * 0.025
    y_text    = y_bracket + y_range * 0.05

    ax.plot([1, 1, 2, 2], [y_bracket, y_tick, y_tick, y_bracket],
            color="black", linewidth=1.1)

    sig = "***" if p < 0.001 else ("**" if p < 0.01 else ("*" if p < ALPHA else "n.s."))
    ax.text(1.5, y_text,
            f"{sig}   p = {p:.4f}\nd = {abs(d):.2f}  ({effect_label(d)})",
            ha="center", va="bottom", fontsize=8, color="black",
            linespacing=1.5)

    ax.set_xticks([1, 2])
    ax.set_xticklabels([name_a.replace("_", "\n"), name_b.replace("_", "\n")],
                       fontsize=8.5)
    ax.set_title(title, pad=8)
    ax.set_ylabel("Final Fitness")
    ax.set_axisbelow(True)

    for x, data in [(1, data_a), (2, data_b)]:
        ax.text(x, ax.get_ylim()[0] + y_range * 0.01,
                f"n={len(data)}", ha="center", va="bottom",
                fontsize=7.5, color="#555555")


def main():
    configs = load_configs(RESULTS_FILE)

    cga50   = configs["CGA_mut50"]
    cga80   = configs["CGA_mut80"]
    rdiga50 = configs["RDIGA_mut50"]
    rdiga80 = configs["RDIGA_mut80"]

    fig, axes = plt.subplots(2, 2, figsize=(10, 11))

    fig.suptitle(
        "CGA vs. RDIGA — Final Fitness Distribution (500 Generations, 15 Runs, Seed 7)\n"
        "Box = IQR  |  White line = median  |  Points = individual runs",
        fontsize=11, fontweight="bold", y=0.995
    )

    draw_boxplot(axes[0][0],
                 [("CGA_mut50", cga50), ("RDIGA_mut50", rdiga50)],
                 "A1) Algorithm Effect  |  μ = 50 %")
    draw_boxplot(axes[0][1],
                 [("CGA_mut80", cga80), ("RDIGA_mut80", rdiga80)],
                 "A2) Algorithm Effect  |  μ = 80 %")
    draw_boxplot(axes[1][0],
                 [("CGA_mut50", cga50), ("CGA_mut80", cga80)],
                 "B1) Mutation Rate Effect  |  CGA")
    draw_boxplot(axes[1][1],
                 [("RDIGA_mut50", rdiga50), ("RDIGA_mut80", rdiga80)],
                 "B2) Mutation Rate Effect  |  RDIGA")

    legend_handles = [
        mpatches.Patch(color="#2166AC", alpha=0.85, label="CGA"),
        mpatches.Patch(color="#D6604D", alpha=0.85, label="RDIGA"),
    ]
    fig.legend(handles=legend_handles, loc="lower center", ncol=2,
               fontsize=9, frameon=False, bbox_to_anchor=(0.5, -0.01))

    plt.tight_layout(rect=[0, 0.03, 1, 0.97], h_pad=3.5, w_pad=2.5)
    plt.savefig(OUTPUT_FILE, dpi=180, bbox_inches="tight", facecolor="white")
    print(f"Saved: {OUTPUT_FILE}")


if __name__ == "__main__":
    main()
