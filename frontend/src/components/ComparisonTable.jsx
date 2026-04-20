const LABELS = {
  CGA_mut50:   'CGA  μ=50%',
  CGA_mut80:   'CGA  μ=80%',
  RDIGA_mut50: 'RDIGA  μ=50%',
  RDIGA_mut80: 'RDIGA  μ=80%',
}
const COLORS = {
  CGA_mut50:   '#1f77b4',
  CGA_mut80:   '#ff7f0e',
  RDIGA_mut50: '#2ca02c',
  RDIGA_mut80: '#d62728',
}

export default function ComparisonTable({ results }) {
  const worstFitness = Math.max(...results.map(r => r.avg_final_fitness))
  const bestIdx      = results.reduce(
    (bi, r, i) => r.avg_final_fitness < results[bi].avg_final_fitness ? i : bi, 0
  )

  return (
    <div className="card">
      <h2 className="card-title">Comparison Summary</h2>
      <p className="card-sub">Average over all runs — ★ marks the best configuration</p>
      <div className="table-wrap">
        <table className="cmp-table">
          <thead>
            <tr>
              <th>Configuration</th>
              <th>Avg Fitness</th>
              <th>± Std</th>
              <th>Avg Collisions</th>
              <th>Avg Path Length</th>
              <th>Avg Runtime (s)</th>
              <th>Improv. vs Worst</th>
            </tr>
          </thead>
          <tbody>
            {results.map((r, i) => {
              const pct = ((worstFitness - r.avg_final_fitness) / worstFitness * 100).toFixed(1)
              const best = i === bestIdx
              const color = COLORS[r.config_name]
              return (
                <tr key={r.config_name} className={best ? 'best-row' : ''}>
                  <td>
                    <span className="config-dot" style={{ background: color }} />
                    {best && '★ '}{LABELS[r.config_name]}
                  </td>
                  <td className={best ? 'best-cell' : ''}>{r.avg_final_fitness.toFixed(2)}</td>
                  <td>{r.std_final_fitness.toFixed(2)}</td>
                  <td>{r.avg_obstacle_collisions.toFixed(1)}</td>
                  <td>{r.avg_path_length.toFixed(1)}</td>
                  <td>{r.avg_runtime_seconds.toFixed(2)}</td>
                  <td className="improv">+{pct}%</td>
                </tr>
              )
            })}
          </tbody>
        </table>
      </div>
    </div>
  )
}
