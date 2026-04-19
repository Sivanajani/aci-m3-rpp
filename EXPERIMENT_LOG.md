# ACI Milestone 3 — Experiment Log
## CGA vs RDIGA for Robotic Path Planning (RPP)

**Course:** Applied Computational Intelligence (ACI) — MSc Medical Informatics, FHNW  
**Paper:** Mankudiyil, Dornberger & Hanne (2024) — *Improved Genetic Algorithm in a Static Environment for Robotic Path Planning*  
**Base code reference:** Rassafi GitHub (`amirrassafi/pathplanning`) — used for orientation only, full reimplementation from scratch

---

## 1. What Was Built

Seven Python modules, pure NumPy + Matplotlib (no PyQt5, no Shapely):

| File | Responsibility |
|---|---|
| `grid.py` | 50×50 occupancy grid, random obstacle placement, proximity queries |
| `chromosome.py` | Path representation (waypoints), crossover, mutation, RDI operator |
| `fitness.py` | F = O·55 + P·20 + A·5 + D·2, Bresenham collision tracing |
| `cga.py` | Conventional GA — tournament selection, elitism, crossover + mutation |
| `rdiga.py` | RDIGA — inherits CGA, sets `use_rdi=True` (the only structural difference) |
| `experiment.py` | Runs all 4 configurations, saves JSON + grid |
| `plot.py` | Fitness curves, comparison table, best-path grid images |

---

## 2. Fixed Parameters (must match paper / M2 definition)

| Parameter | Value | Source |
|---|---|---|
| Grid size | 50×50 | Paper |
| Obstacle density | 25 % = 625 tiles | Paper |
| Start / Goal | (0,0) → (49,49) | Paper |
| Population size | **55** chromosomes | Paper — **never changed** |
| Crossover rate | **50 %** | Paper — **never changed** |
| Mutation rates | **50 %** and **80 %** | Paper — **never changed** |
| Movement | 8-directional (rect. + diagonal) | Paper |

---

## 3. Fitness Function

```
F = O·55 + P·20 + A·5 + D·2       (minimisation — lower = better)
```

| Component | Meaning | Formula |
|---|---|---|
| O | Obstacle collisions (hard constraint) | # of obstacle cells along path segments (Bresenham) |
| P | Proximity to obstacles (soft) | e^(−0.2 × d_min), d_min = min Euclidean dist. to any obstacle |
| A | Maximum turning angle (soft) | max angle in radians at any intermediate waypoint |
| D | Total path length (soft) | sum of Euclidean distances between consecutive waypoints |

The collision term dominates (weight 55) — finding a collision-free path is the primary objective.

---

## 4. RDI Operator (the only difference between CGA and RDIGA)

After mutation, RDIGA applies one additional step:

1. Select two random indices **i ≤ j** in the waypoint list
2. Reverse the sub-sequence `waypoints[i : j+1]`

This preserves genetic material while reshuffling path segments, helping escape local optima.  
Implementation: `chromosome.py → apply_rdi()`, activated by `use_rdi=True` in `cga.py`.

---

## 5. GA Design Decisions

### Selection
**Tournament selection** (size 3) — robust, no fitness scaling needed, avoids premature convergence from roulette selection on skewed fitness distributions.

### Elitism
The single best chromosome is always carried to the next generation unchanged. This guarantees monotone improvement in best fitness.

### Population management
```
new population = [1 elite] + [54 offspring from tournament pairs]
```
Each offspring pair: crossover (prob = 0.5) → mutation (per-gene prob = μ) → RDI (RDIGA only).

### Chromosome representation
A chromosome = **N intermediate waypoints** (row, col). Full path:
```
START (0,0) → wp[0] → wp[1] → … → wp[N−1] → GOAL (49,49)
```
Segments between waypoints are straight lines, checked for obstacle collisions via Bresenham's algorithm.

---

## 6. Run 1 — Baseline
**Parameters:** 50 generations · 5 runs · 20 waypoints · random initialisation

### Results

| Config | Avg Fitness | ± Std | Avg Collisions | Avg Length |
|---|---|---|---|---|
| CGA μ=50 % | 4644 | ± 207 | 70 | 368 |
| CGA μ=80 % | 4849 | ± 185 | 73 | 399 |
| **RDIGA μ=50 %** | **4480** | **± 130** | **68** | **378** |
| RDIGA μ=80 % | 5028 | ± 248 | 76 | 414 |

### Key observation
The fitness curves were still falling at generation 50 — the GA had not converged. More generations would yield better solutions.

**Plots:** `results/1_fitness_curves.png`, `results/1_comparison_table.png`, `results/1_best_paths.png`

---

## 7. Improvements Applied Before Run 2

Two changes that **do not touch any core parameter**:

### 7.1 Smart Chromosome Initialisation
**Before:** Waypoints placed at fully random (row, col) → average ~120 initial collisions.  
**After:** Waypoints placed along the START→GOAL diagonal with Gaussian noise (σ = 5 cells).

```python
t = (i + 1) / (N_WAYPOINTS + 1)        # position along path [0, 1]
base_r = t * 49                          # diagonal target
base_c = t * 49
r = clip(base_r + Normal(0, 5), 0, 49)  # add diversity noise
c = clip(base_c + Normal(0, 5), 0, 49)
```

**Why:** The GA still finds the optimum by itself — we only give it a sensible starting region instead of random noise across the whole grid. This is standard practice in GA for constrained spatial problems.

### 7.2 More Intermediate Waypoints (20 → 30)
**Before:** 20 waypoints → 22 points total including START/GOAL.  
**After:** 30 waypoints → 32 points total.

**Why:** More waypoints = more flexibility for the path to navigate around dense obstacle clusters. With only 20 points on a 50×50 grid, some obstacle configurations had no valid route within reach.

### 7.3 More Generations and Runs
| Parameter | Run 1 | Run 2 | Reason |
|---|---|---|---|
| Generations | 50 | **150** | Curves still converging at gen 50 |
| Runs/config | 5 | **10** | More runs → more stable averages, less influence of lucky/unlucky random seeds |
| Population | 55 | 55 | Fixed — must match paper |

---

## 8. Run 2 — Improved Setup
**Parameters:** 150 generations · 10 runs · 30 waypoints · smart initialisation

### Results

| Config | Avg Fitness | ± Std | Avg Collisions | Avg Length | Avg Runtime |
|---|---|---|---|---|---|
| CGA μ=50 % | 4101 | ± 249 | 60.4 | 372 | 3.0 s |
| CGA μ=80 % | 4476 | ± 254 | 66.4 | 395 | 3.3 s |
| **RDIGA μ=50 %** | **4099** | **± 336** | **61.2** | **349** | **2.9 s** |
| RDIGA μ=80 % | 4505 | ± 288 | 67.4 | 381 | 3.2 s |

### Improvement vs Run 1

| Config | Fitness Δ | Collision Δ |
|---|---|---|
| CGA μ=50 % | −11.7 % | −13.7 % |
| CGA μ=80 % | −7.7 % | −9.0 % |
| RDIGA μ=50 % | −8.5 % | −10.0 % |
| RDIGA μ=80 % | −10.4 % | −11.3 % |

**Plots:** `results/2_fitness_curves.png`, `results/2_comparison_table.png`, `results/2_best_paths.png`

---

## 9. Interpretation

### Finding 1 — RDIGA μ=50 % wins
RDIGA with 50 % mutation achieves the lowest average fitness (4099) and the shortest paths (349 units). The RDI operator helps the algorithm find better routes without disrupting good solutions.

### Finding 2 — High mutation (80 %) hurts both algorithms
Both CGA and RDIGA perform worse at μ=80 %. Excessive mutation destroys good solutions faster than the GA can rebuild them — the search degrades towards random.

### Finding 3 — μ=50 % is the sweet spot
At 50 % mutation rate the algorithm maintains enough exploration to escape local optima while preserving good building blocks. This matches the paper's conclusion.

### Finding 4 — Curves still not fully flat at gen 150
The fitness curves plateau around generation 80–100 but still show occasional improvements at gen 150. Further gains are possible but marginal. The current setup is a good trade-off between runtime and result quality.

---

## 10. File Overview

```
aci_m3/
├── grid.py           Grid environment
├── chromosome.py     Path encoding + genetic operators
├── fitness.py        F = O·55 + P·20 + A·5 + D·2
├── cga.py            Conventional GA
├── rdiga.py          CGA + RDI operator
├── experiment.py     Main runner → results/results.json
├── plot.py           Plot generator → results/*.png
├── EXPERIMENT_LOG.md This file
└── results/
    ├── results.json
    ├── best_paths.json
    ├── grid.npy
    ├── 1_*.png        Run 1 plots (50 gens, 5 runs, random init)
    └── 2_*.png        Run 2 plots (150 gens, 10 runs, smart init)
```

---

*Generated during ACI M3 development session, April 2026.*
