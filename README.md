# ACI — CGA vs RDIGA for Robotic Path Planning

**Author:** Sivanajani Sivakumar  
**Email:** sivanajani.sivakumar@students.fhnw.ch  
**Programme:** MSc Medical Informatics · FHNW · April 2026  
**Course:** Applied Computational Intelligence (ACI)  
**Paper:** Mankudiyil, Dornberger & Hanne (2024) — *Improved Genetic Algorithm in a Static Environment for Robotic Path Planning*

---

## Base Code

This project builds on the original path planning implementation by **Amir Rassafi**:

> GitHub: [amirrassafi/pathplanning](https://github.com/amirrassafi/pathplanning)

The original code (`pp.py`, `ui/`) implements a basic Genetic Algorithm for path planning with a PyQt5 GUI, using Shapely polygons for obstacle representation. It served as a reference for understanding the GA structure and fitness function design.

---

## What Was Extended

| What | How it was extended |
|---|---|
| **Grid environment** | Replaced Shapely polygons with a clean 50×50 NumPy binary grid (25% obstacle density) |
| **Chromosome** | New waypoint-based path encoding (30 intermediate points) with two-point crossover, per-gene mutation, and the RDI operator |
| **Fitness function** | Implemented exactly as per paper: `F = O·55 + P·20 + A·5 + D·2` with Bresenham collision tracing |
| **CGA** | Full Conventional GA with tournament selection, elitism, configurable crossover/mutation rates |
| **RDIGA** | Extended CGA with the Random Domain Inversion operator — the only structural difference from CGA |
| **Experiment runner** | Automated 4-configuration × 15-run experiment with JSON output, reproducible via fixed seed (7) |
| **Plots** | matplotlib plots: fitness convergence curves (±1 std band), comparison table, best path grids |
| **Statistical analysis** | Mann-Whitney U test, Welch t-test, Cohen's d effect size for algorithm and mutation rate comparisons |
| **Web frontend** | React + Vite UI with live progress, interactive parameter controls, recharts visualisations |
| **REST API backend** | FastAPI backend that runs the experiment and streams progress to the frontend |

---

## Project Structure

```
aci_m3/
│
├── pp.py                    # Original Rassafi base code (reference only)
├── ui/                      # Original Rassafi PyQt5 UI files (reference only)
│
├── grid.py                  # 50×50 NumPy occupancy grid, obstacle placement
├── chromosome.py            # Path encoding: waypoints, crossover, mutation, RDI
├── fitness.py               # F = O·55 + P·20 + A·5 + D·2 (Bresenham collision tracing)
├── cga.py                   # Conventional Genetic Algorithm
├── rdiga.py                 # RDIGA = CGA + Random Domain Inversion operator
├── experiment.py            # Runs all 4 configs × 15 runs, saves results to results/
├── plot.py                  # Fitness curves, comparison table, best path grids
├── statistical_tests.py     # Mann-Whitney U, Welch t-test, Cohen's d
├── plot_statistics.py       # Boxplot figures with significance brackets
├── plot_stripplot.py        # Stripplot figures with individual run values
│
├── backend/
│   ├── main.py              # FastAPI REST API (runs experiment, streams progress)
│   └── requirements.txt
│
├── frontend/
│   ├── src/
│   │   ├── App.jsx          # Main layout, state management, polling
│   │   ├── App.css          # Animations, design system
│   │   └── components/
│   │       ├── ConfigPanel.jsx     # Gens / Runs / Seed inputs + Run button
│   │       ├── ProgressBar.jsx     # Live progress bar
│   │       ├── ProgressLog.jsx     # Live terminal-style log
│   │       ├── FitnessCurves.jsx   # Recharts line chart (all 4 configs)
│   │       ├── ComparisonTable.jsx # Summary table with best-row highlight
│   │       ├── PathGrid.jsx        # Canvas 50×50 grid with path overlay
│   │       └── DownloadPanel.jsx   # Download JSON / CSV / PNG
│   ├── vite.config.js
│   └── package.json
│
├── results/                 # Generated outputs (gitignored)
│   ├── 7seed_200gens_15runs_results.json   # Main experiment results (200 gens)
│   ├── 7seed_500gens_15runs_results.json   # Extended run results (500 gens)
│   ├── 7seed_200gens_15runs_*.png          # Plots for 200-gen run
│   ├── 200_statistical_boxplots.png        # Statistical boxplots (200 gens)
│   └── 200_statistical_stripplot.png       # Stripplot with individual run values
│
├── INSTALL.md               # One-page installation and run guide
├── EXPERIMENT_LOG.md        # Full experiment documentation with results
├── requirements.txt         # Python dependencies
└── .gitignore
```

---

## Experiment Parameters (Final Run)

| Parameter | Value |
|---|---|
| Grid size | 50×50 |
| Obstacle density | 25% (625 tiles) |
| Start / Goal | (0, 0) → (49, 49) |
| Population size | 55 |
| Crossover rate | 50% |
| Mutation rates | 50% and 80% |
| Generations | 200 |
| Runs per config | 15 |
| Random seed | 7 |

### Four Configurations

| # | Algorithm | Mutation Rate | Avg Final Fitness |
|---|---|---|---|
| 1 | CGA | 50% | 4117.70 |
| 2 | CGA | 80% | 4530.31 |
| 3 | RDIGA | 50% | 4009.83 |
| 4 | RDIGA | 80% | 4535.43 |

### Fitness Function

```
F = O·55  +  P·20  +  A·5  +  D·2     (minimisation — lower is better)

O = obstacle collisions (Bresenham line tracing)
P = e^(−0.2 × min_distance_to_obstacle)
A = maximum turning angle (radians)
D = total Euclidean path length
```

### RDI Operator (RDIGA only)

After mutation, select two random indices `i ≤ j` and reverse `waypoints[i:j+1]`. This is the **only structural difference** between CGA and RDIGA.

---

## Key Statistical Findings

All tests run on `results/7seed_200gens_15runs_results.json` (n=15 per config, α=0.05):

### A) Algorithm Effect (CGA vs RDIGA, same mutation rate)

| Comparison | U | p-value | Cohen's d | Result |
|---|---|---|---|---|
| CGA 50% vs RDIGA 50% | 138 | 0.2998 | 0.41 (small) | n.s. |
| CGA 80% vs RDIGA 80% | 127 | 0.5614 | 0.02 (negligible) | n.s. |

→ **No significant difference** between CGA and RDIGA.

### B) Mutation Rate Effect (50% vs 80%, same algorithm)

| Comparison | U | p-value | Cohen's d | Result |
|---|---|---|---|---|
| CGA 50% vs CGA 80% | 34 | 0.0012 | 1.53 (large) | ** |
| RDIGA 50% vs RDIGA 80% | 15 | 0.0001 | 2.04 (large) | *** |

→ **μ = 80% significantly outperforms μ = 50%** in both algorithms (large effect).

---

## How to Run

See **[INSTALLATION_GUIDE.md](INSTALLATION_GUIDE.md)** for the full installation and run guide.

---

## References

- Mankudiyil, S., Dornberger, R., & Hanne, T. (2024). *Improved Genetic Algorithm in a Static Environment for Robotic Path Planning.* FHNW.
- Rassafi, A. (2018). *Path Planning Base Code.* [github.com/amirrassafi/pathplanning](https://github.com/amirrassafi/pathplanning)
