import { useEffect, useRef } from 'react'

export default function ProgressLog({ log, status }) {
  const bottomRef = useRef(null)

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [log])

  if (!log.length && status === 'idle') return null

  return (
    <div className="card log-card">
      <h2 className="card-title">
        Progress
        {status === 'running' && <span className="spinner" />}
        {status === 'done'    && <span className="badge done">Done</span>}
        {status === 'error'   && <span className="badge error">Error</span>}
      </h2>
      <div className="log-box">
        {log.map((line, i) => (
          <div key={i} className={`log-line ${line.startsWith('ERROR') ? 'log-error' : ''}`}>
            {line}
          </div>
        ))}
        <div ref={bottomRef} />
      </div>
    </div>
  )
}
