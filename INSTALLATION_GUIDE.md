# Installation Guide
## ACI M3 — Robotic Path Planning: CGA vs. RDIGA
**Author:** Sivanajani Sivakumar · MSc Medical Informatics · FHNW · 2026

---

## Required Software

| Software | Version | Download |
|----------|---------|----------|
| Python | 3.10 or higher | python.org |
| Node.js | 18 or higher | nodejs.org |
| npm | 9 or higher | included with Node.js |

---

## Installation

**Step 1 — Install Python packages**
```bash
pip install fastapi uvicorn[standard] numpy scipy matplotlib
```

**Step 2 — Install frontend packages** (from the project root folder)
```bash
cd frontend
npm install
cd ..
```

---

## Running the Prototype

Two terminals must be open simultaneously, both starting from the **project root folder**.

**Terminal 1 — Backend:**
```bash
uvicorn backend.main:app --reload
```
The API starts at `http://127.0.0.1:8000`

**Terminal 2 — Frontend:**
```bash
cd frontend
npm run dev
```
Open the application in a browser at **`http://localhost:5173`**

In the interface: select algorithm (CGA / RDIGA), mutation rate, and number of generations, then click **Run**.

---

## Command-Line Usage (optional)

```bash
python experiment.py                                                  # run all 4 configs
python statistical_tests.py --file results/7seed_200gens_15runs_results.json
python plot_statistics.py                                             # boxplots
python plot_stripplot.py                                              # stripplots
```

---

## Self-Developed Files

| File | Description |
|------|-------------|
| `grid.py` | 50×50 NumPy occupancy grid with Bresenham collision detection |
| `chromosome.py` | Waypoint-based path encoding, crossover, mutation, RDI operator |
| `fitness.py` | Fitness function: F = O×55 + P×20 + A×5 + D×2 |
| `cga.py` | Conventional Genetic Algorithm |
| `rdiga.py` | RDIGA = CGA + Random Domain Inversion operator |
| `experiment.py` | Automated experiment runner (4 configs × 15 runs, JSON output) |
| `plot.py` | Fitness curves, comparison table, best path visualisation |
| `statistical_tests.py` | Mann-Whitney U, Welch t-test, Cohen's d |
| `plot_statistics.py` | Statistical boxplots with significance annotations |
| `plot_stripplot.py` | Stripplots with individual run values |
| `backend/main.py` | FastAPI server — endpoints: `/run`, `/status`, `/results` |
| `frontend/src/App.jsx` | React main application |
| `frontend/src/components/` | UI components: ConfigPanel, FitnessCurves, PathGrid, … |
