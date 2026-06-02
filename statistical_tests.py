"""
Statistical Analysis: CGA vs RDIGA — Fitness Comparison
========================================================

Tests:
  1. Mann-Whitney U  — main method, distribution-free, robust at n=15/20
  2. Welch t-Test    — cross-check using mean/std (no normality assumption required)
  3. Cohen's d       — effect size: shows how large the difference actually is

Comparisons:
  A) Algorithm effect    : CGA50 vs RDIGA50 | CGA80 vs RDIGA80
  B) Mutation rate effect: CGA50 vs CGA80   | RDIGA50 vs RDIGA80
"""

import argparse
import json
import numpy as np
from scipy import stats


# ─── Configuration ────────────────────────────────────────────────────────────

_parser = argparse.ArgumentParser()
_parser.add_argument("--file", default="results/7seed_500gens_15runs_results.json")
_args = _parser.parse_args()

RESULTS_FILE = _args.file
ALPHA = 0.05  # significance level


# ─── Load data ────────────────────────────────────────────────────────────────

def load_configs(path: str) -> dict:
    """Reads JSON and returns dict {config_name: [fitness_values]}."""
    with open(path) as f:
        data = json.load(f)
    return {entry["config_name"]: entry["all_final_fitness"] for entry in data}


# ─── Test 3: Cohen's d (effect size) ──────────────────────────────────────────
#
# Cohen's d measures how large the difference between two groups is —
# independent of the p-value. A small p can still represent a tiny effect.
#
# Formula: d = (mean_A - mean_B) / pooled standard deviation
#
# Interpretation:
#   |d| < 0.2  → negligible
#   |d| < 0.5  → small
#   |d| < 0.8  → medium
#   |d| >= 0.8 → large

def cohen_d(a, b):
    pooled_std = np.sqrt((np.std(a, ddof=1) ** 2 + np.std(b, ddof=1) ** 2) / 2)
    return (np.mean(a) - np.mean(b)) / pooled_std


def effect_label(d):
    d = abs(d)
    if d < 0.2: return "negligible"
    if d < 0.5: return "small"
    if d < 0.8: return "medium"
    return "large"


# ─── All three tests combined ─────────────────────────────────────────────────

def run_tests(a, b, name_a, name_b):
    print(f"{'─'*58}")
    print(f"  {name_a}  vs  {name_b}")
    print(f"{'─'*58}")
    print(f"  {name_a:<15}  n={len(a):>2}  Median={np.median(a):>8.2f}  M={np.mean(a):>8.2f}  SD={np.std(a, ddof=1):>7.2f}")
    print(f"  {name_b:<15}  n={len(b):>2}  Median={np.median(b):>8.2f}  M={np.mean(b):>8.2f}  SD={np.std(b, ddof=1):>7.2f}")
    print()

    # ── Test 1: Mann-Whitney U ─────────────────────────────────────────────────
    #
    # Compares the rank distributions of two independent groups.
    # No normality assumption required → ideal for small samples (n=15-20).
    # H0: both groups come from the same distribution.
    # p < alpha → reject H0 → statistically significant difference.
    #
    # Z-value: normal approximation of the U statistic for reporting.

    mw_stat, mw_p = stats.mannwhitneyu(a, b, alternative="two-sided")
    n = len(a) + len(b)
    mu_U    = len(a) * len(b) / 2
    sigma_U = np.sqrt(len(a) * len(b) * (n + 1) / 12)
    z       = (mw_stat - mu_U) / sigma_U

    sig_mw = "*" if mw_p < ALPHA else "n.s."
    print(f"  [1] Mann-Whitney U  U={mw_stat:>5.0f}  Z={z:>6.3f}  p={mw_p:.4f}  {sig_mw}")

    # ── Test 2: Welch t-Test ───────────────────────────────────────────────────
    #
    # Parametric test: compares the means of two groups.
    # Welch variant (equal_var=False) allows unequal variances →
    # more robust than the classic t-test.
    # Used here as a cross-check for the Mann-Whitney U result.
    # If both tests agree → result is reliable.

    t_stat, t_p = stats.ttest_ind(a, b, equal_var=False)

    sig_t = "*" if t_p < ALPHA else "n.s."
    print(f"  [2] Welch t-Test    t={t_stat:>6.3f}          p={t_p:.4f}  {sig_t}")

    # ── Test 3: Cohen's d ──────────────────────────────────────────────────────

    d = cohen_d(a, b)
    print(f"  [3] Cohen's d       d={d:>6.3f}  → effect: {effect_label(d)}")
    print()


# ─── Main ─────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    configs = load_configs(RESULTS_FILE)

    cga50   = configs["CGA_mut50"]
    cga80   = configs["CGA_mut80"]
    rdiga50 = configs["RDIGA_mut50"]
    rdiga80 = configs["RDIGA_mut80"]

    print(f"\nFile   : {RESULTS_FILE}")
    print(f"Alpha  : {ALPHA}  (* = significant, n.s. = not significant)\n")

    # A) Algorithm effect — answers: "Is RDIGA better than CGA?"
    print("=== A) Algorithm Effect (same mutation rate) ===\n")
    run_tests(cga50,   rdiga50, "CGA_mut50",  "RDIGA_mut50")
    run_tests(cga80,   rdiga80, "CGA_mut80",  "RDIGA_mut80")

    # B) Mutation rate effect — answers: "Does mu=80% make a difference?"
    print("=== B) Mutation Rate Effect (same algorithm) ===\n")
    run_tests(cga50,   cga80,   "CGA_mut50",  "CGA_mut80")
    run_tests(rdiga50, rdiga80, "RDIGA_mut50", "RDIGA_mut80")
