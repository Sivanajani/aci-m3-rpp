export default function ConfigPanel({ params, setParams, onRun, status }) {
  const running = status === 'running'

  return (
    <div className="card">
      <h2 className="card-title">Experiment Setup</h2>

      <div className="field">
        <label>Generations</label>
        <input
          type="number" min={10} max={500} step={10}
          value={params.n_generations}
          disabled={running}
          onChange={e => setParams(p => ({ ...p, n_generations: +e.target.value }))}
        />
      </div>

      <div className="field">
        <label>Runs per config</label>
        <input
          type="number" min={1} max={30} step={1}
          value={params.n_runs}
          disabled={running}
          onChange={e => setParams(p => ({ ...p, n_runs: +e.target.value }))}
        />
      </div>

      <div className="field">
        <label>Random seed</label>
        <input
          type="number" min={0}
          value={params.seed}
          disabled={running}
          onChange={e => setParams(p => ({ ...p, seed: +e.target.value }))}
        />
      </div>

      <div className="fixed-params">
        <span>Population: <b>55</b></span>
        <span>Crossover: <b>50%</b></span>
        <span>Mutation: <b>50% &amp; 80%</b></span>
        <span>Grid: <b>50×50</b></span>
      </div>

      <button
        className={`run-btn ${running ? 'running' : ''}`}
        onClick={onRun}
        disabled={running}
      >
        {running ? 'Running…' : 'Run Experiment'}
      </button>
    </div>
  )
}
