import { useState, useEffect, useRef } from 'react'
import ConfigPanel     from './components/ConfigPanel.jsx'
import ProgressLog     from './components/ProgressLog.jsx'
import FitnessCurves   from './components/FitnessCurves.jsx'
import ComparisonTable from './components/ComparisonTable.jsx'
import PathGrid        from './components/PathGrid.jsx'
import DownloadPanel   from './components/DownloadPanel.jsx'
import ProgressBar     from './components/ProgressBar.jsx'

const API = import.meta.env.VITE_API_URL

export default function App() {
  const [params, setParams] = useState({ n_generations: 200, n_runs: 15, seed: 7 })
  const [status, setStatus] = useState('idle')
  const [log,    setLog]    = useState([])
  const [data,   setData]   = useState(null)   // { results, paths, grid }
  const pollRef = useRef(null)

  // ── start experiment ────────────────────────────────────────────────
  async function handleRun() {
    setData(null)
    setLog([])
    setStatus('running')

    await fetch(`${API}/run`, {
      method : 'POST',
      headers: { 'Content-Type': 'application/json' },
      body   : JSON.stringify(params),
    })

    // Start polling /status every 1.5 s
    pollRef.current = setInterval(async () => {
      const res = await fetch(`${API}/status`)
      const s   = await res.json()
      setLog(s.log ?? [])
      setStatus(s.status)

      if (s.status === 'done') {
        clearInterval(pollRef.current)
        const r = await fetch(`${API}/results`)
        setData(await r.json())
      }
      if (s.status === 'error') {
        clearInterval(pollRef.current)
      }
    }, 1500)
  }

  useEffect(() => () => clearInterval(pollRef.current), [])

  return (
    <div className="app">

      {/* ── Header ─────────────────────────────────────────────────── */}
      <header className="app-header">
        <div>
          <h1>CGA vs RDIGA — Robotic Path Planning</h1>
          <p>Applied Computational Intelligence · Milestone 3</p>
        </div>
        <div className="header-meta">
          <span className="header-name">Sivanajani Sivakumar</span>
          <span className="header-detail">sivanajani.sivakumar@students.fhnw.ch</span>
          <span className="header-detail">MSc Medical Informatics · FHNW · April 2026</span>
        </div>
      </header>

      {/* ── Main layout ────────────────────────────────────────────── */}
      <div className="main-layout">

        {/* Left column: config + log */}
        <aside className="sidebar">
          <ConfigPanel
            params={params}
            setParams={setParams}
            onRun={handleRun}
            status={status}
          />
          <ProgressBar log={log} params={params} status={status} />
          <ProgressLog log={log} status={status} />
        </aside>

        {/* Right column: results */}
        <main className="results-col">
          {!data && status === 'idle' && (
            <div className="placeholder">
              <p>Configure the experiment on the left and click <b>Run Experiment</b>.</p>
              <p className="hint">
                Generations, runs, and seed are fully adjustable.<br />
                Population (55), crossover (50%), and mutation rates (50%/80%)
                are fixed per the paper.
              </p>
            </div>
          )}

          {!data && status === 'running' && (
            <div className="placeholder">
              <div className="big-spinner" />
              <p>Experiment running — results appear here when done.</p>
            </div>
          )}

          {data && (
            <div className="results-animate">
              <FitnessCurves   results={data.results} />
              <ComparisonTable results={data.results} />
              <PathGrid
                results={data.results}
                paths={data.paths}
                grid={data.grid}
              />
              <DownloadPanel
                results={data.results}
                paths={data.paths}
                grid={data.grid}
              />
            </div>
          )}
        </main>
      </div>
    </div>
  )
}
