# ACI Milestone 3 — CGA vs RDIGA for Robotic Path Planning

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

The original Rassafi code was completely reimplemented based on the paper's parameters. The following was built on top of the reference:

| What | How it was extended |
|---|---|
| **Grid environment** | Replaced Shapely polygons with a clean 50×50 NumPy binary grid (25% obstacle density) |
| **Chromosome** | New waypoint-based path encoding (20 intermediate points) with two-point crossover, per-gene mutation, and the RDI operator |
| **Fitness function** | Implemented exactly as per paper: `F = O·55 + P·20 + A·5 + D·2` with Bresenham collision tracing |
| **CGA** | Full Conventional GA with tournament selection, elitism, configurable crossover/mutation rates |
| **RDIGA** | Extended CGA with the Random Domain Inversion operator — the only structural difference from CGA |
| **Experiment runner** | Automated 4-configuration × N-run experiment with JSON output, reproducible via fixed seed |
| **Plots** | matplotlib plots: fitness convergence curves (±1 std band), comparison table, best path grids |
| **Web frontend** | React + Vite UI with live progress, interactive parameter controls, recharts visualisations |
| **REST API backend** | FastAPI backend that runs the experiment and streams progress to the frontend |

---

## Project Structure

```
aci_m3/
│
├── pp.py                  # Original Rassafi base code (reference only)
├── ui/                    # Original Rassafi PyQt5 UI files (reference only)
│
├── grid.py                # 50×50 NumPy occupancy grid, obstacle placement
├── chromosome.py          # Path encoding: waypoints, crossover, mutation, RDI
├── fitness.py             # F = O·55 + P·20 + A·5 + D·2 (Bresenham collision tracing)
├── cga.py                 # Conventional Genetic Algorithm
├── rdiga.py               # RDIGA = CGA + Random Domain Inversion operator
├── experiment.py          # Runs all 4 configs, saves results to results/
├── plot.py                # Generates PNG plots from results/results.json
│
├── backend/
│   ├── main.py            # FastAPI REST API (runs experiment, streams progress)
│   └── requirements.txt
│
├── frontend/
│   ├── src/
│   │   ├── App.jsx        # Main layout, state management, polling
│   │   ├── App.css        # Animations, design system
│   │   └── components/
│   │       ├── ConfigPanel.jsx    # Gens / Runs / Seed inputs + Run button
│   │       ├── ProgressBar.jsx    # Live progress bar
│   │       ├── ProgressLog.jsx    # Live terminal-style log
│   │       ├── FitnessCurves.jsx  # Recharts line chart (all 4 configs)
│   │       ├── ComparisonTable.jsx# Summary table with best-row highlight
│   │       ├── PathGrid.jsx       # Canvas 50×50 grid with path overlay
│   │       └── DownloadPanel.jsx  # Download JSON / CSV / PNG
│   ├── vite.config.js
│   └── package.json
│
├── results/               # Generated outputs (gitignored)
│   ├── results.json
│   ├── best_paths.json
│   ├── grid.npy
│   └── *.png
│
├── EXPERIMENT_LOG.md      # Full experiment documentation with results
├── requirements.txt       # Python dependencies
└── .gitignore
```

---

## Experiment Parameters

| Parameter | Value | Note |
|---|---|---|
| Grid | 50×50 | Fixed per paper |
| Obstacle density | 25% (625 tiles) | Fixed per paper |
| Start / Goal | (0,0) → (49,49) | Fixed per paper |
| Population size | 55 | Fixed per paper |
| Crossover rate | 50% | Fixed per paper |
| Mutation rates | 50% and 80% | Two experiments each |
| Generations | configurable (default 200) | Baseline 50 per paper |
| Runs per config | configurable (default 15) | Baseline 5 per paper |

### Four Configurations

| # | Algorithm | Mutation Rate |
|---|---|---|
| 1 | CGA | 50% |
| 2 | CGA | 80% |
| 3 | RDIGA | 50% |
| 4 | RDIGA | 80% |

### Fitness Function

```
F = O·55  +  P·20  +  A·5  +  D·2     (minimisation)

O = obstacle collisions (Bresenham line tracing)
P = e^(−0.2 × min_distance_to_obstacle)
A = maximum turning angle (radians)
D = total Euclidean path length
```

### RDI Operator (RDIGA only)

After mutation, select two random indices `i ≤ j` and reverse `waypoints[i:j+1]`. This is the **only structural difference** between CGA and RDIGA.

---

## How to Run

### Option A — Command Line (Python only)

```bash
# Setup
git clone https://github.com/Sivanajani/aci-m3-rpp.git
cd aci-m3-rpp
python -m venv venv && source venv/bin/activate
pip install numpy matplotlib fastapi "uvicorn[standard]"

# Run experiment
python experiment.py

# Generate plots
python plot.py
# → results/fitness_curves.png
# → results/comparison_table.png
# → results/best_paths.png
```

### Option B — Web App (React + FastAPI)

**Terminal 1 — Backend:**
```bash
source venv/bin/activate
uvicorn backend.main:app --reload --port 8000
```

**Terminal 2 — Frontend:**
```bash
cd frontend
npm install
npm run dev
# → http://localhost:5173
```

The web app allows you to adjust **Generations**, **Runs**, and **Seed** interactively and see live progress as the experiment runs.

---

## References

- Mankudiyil, S., Dornberger, R., & Hanne, T. (2024). *Improved Genetic Algorithm in a Static Environment for Robotic Path Planning.* FHNW.
- Rassafi, A. (2018). *Path Planning Base Code.* [github.com/amirrassafi/pathplanning](https://github.com/amirrassafi/pathplanning)
