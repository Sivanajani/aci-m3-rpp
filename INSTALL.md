# Installation Guide — ACI M3: Robotic Path Planning (CGA vs RDIGA)

## System Requirements

| Component | Version |
|-----------|---------|
| Python    | 3.10 or higher |
| Node.js   | 18 or higher |
| npm       | 9 or higher |

---

## 1 — Install Python Dependencies

```bash
pip install fastapi uvicorn[standard] numpy scipy matplotlib
```

---

## 2 — Install Frontend Dependencies

Navigate into the `frontend` folder and install Node packages:

```bash
cd frontend
npm install
cd ..
```

---

## 3 — Run the Prototype (Web Interface)

Open **two separate terminals**, both starting from the project root folder:

**Terminal 1 — Backend (API server):**
```bash
uvicorn backend.main:app --reload
```
→ Run from the **project root** (not inside `backend/`). API runs at `http://127.0.0.1:8000`

**Terminal 2 — Frontend (UI):**
```bash
cd frontend
npm run dev
```
→ Open in browser: **`http://localhost:5173`**

> Both terminals must stay open while using the app.

In the web interface, select algorithm (CGA / RDIGA), mutation rate, and number of generations, then click **Run** to start an experiment.

---

## 4 — Run Experiments via Command Line (optional)

```bash
# Run all 4 configurations (200 gens, 15 runs, seed 7) → results/results.json
python experiment.py

# Statistical analysis — defaults to 500-gen results; use --file to switch
python statistical_tests.py
python statistical_tests.py --file results/7seed_200gens_15runs_results.json

# Generate statistical plots → results/statistical_boxplots.png
python plot_statistics.py

# Generate stripplots → results/statistical_stripplot.png
python plot_stripplot.py
```

---

## Self-Developed Files

| File | Description |
|------|-------------|
| `chromosome.py` | Chromosome representation (waypoint-based path encoding) |
| `fitness.py` | Fitness function: F = O×55 + P×20 + A×5 + D×2 |
| `grid.py` | 50×50 obstacle grid with Bresenham collision detection |
| `cga.py` | Canonical Genetic Algorithm implementation |
| `rdiga.py` | RDIGA: CGA + RDI operator (shuffle + invert gene subset) |
| `experiment.py` | Experiment runner: all 4 configs, 15 runs each, JSON output |
| `plot.py` | Fitness curve and path visualisation |
| `statistical_tests.py` | Mann-Whitney U, Welch t-test, Cohen's d analysis |
| `plot_statistics.py` | Boxplot figures with significance annotations |
| `plot_stripplot.py` | Stripplot figures with individual run values |
| `backend/main.py` | FastAPI server (REST API: /run, /status, /results) |
| `frontend/src/App.jsx` | Main React application |
| `frontend/src/components/` | UI components (ConfigPanel, FitnessCurves, PathGrid, …) |
