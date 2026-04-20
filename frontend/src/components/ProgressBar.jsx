export default function ProgressBar({ log, params, status }) {
  if (status === 'idle') return null

  // Count completed runs from log ("Run X/Y —" lines)
  const completed  = log.filter(l => l.trim().startsWith('Run ')).length
  const total      = (params?.n_runs ?? 10) * 4
  const pct        = status === 'done' ? 100 : Math.min(Math.round((completed / total) * 100), 99)

  return (
    <div className="progress-wrap">
      <div className="progress-header">
        <span>{status === 'done' ? 'Complete' : `Running… ${pct}%`}</span>
        <span className="progress-count">{completed}/{total} runs</span>
      </div>
      <div className="progress-track">
        <div
          className={`progress-fill ${status === 'done' ? 'done' : ''}`}
          style={{ width: `${pct}%` }}
        />
      </div>
    </div>
  )
}
