import { useEffect, useRef } from 'react'

const CELL   = 7          // pixels per grid cell
const SIZE   = 50 * CELL  // canvas size = 350px

const COLORS = {
  CGA_mut50:   '#1f77b4',
  CGA_mut80:   '#ff7f0e',
  RDIGA_mut50: '#2ca02c',
  RDIGA_mut80: '#d62728',
}
const LABELS = {
  CGA_mut50:   'CGA  μ=50%',
  CGA_mut80:   'CGA  μ=80%',
  RDIGA_mut50: 'RDIGA  μ=50%',
  RDIGA_mut80: 'RDIGA  μ=80%',
}

function GridCanvas({ configName, path, grid, result }) {
  const canvasRef = useRef(null)

  useEffect(() => {
    const canvas = canvasRef.current
    if (!canvas) return
    const ctx = canvas.getContext('2d')

    // Draw grid cells
    for (let r = 0; r < 50; r++) {
      for (let c = 0; c < 50; c++) {
        ctx.fillStyle = grid[r][c] === 1 ? '#4a4a4a' : '#ebebeb'
        ctx.fillRect(c * CELL, r * CELL, CELL, CELL)
      }
    }

    // Draw path
    if (path && path.length > 1) {
      ctx.strokeStyle = COLORS[configName]
      ctx.lineWidth   = 2.0
      ctx.lineJoin    = 'round'
      ctx.beginPath()
      ctx.moveTo(path[0][1] * CELL + CELL / 2, path[0][0] * CELL + CELL / 2)
      for (let i = 1; i < path.length; i++) {
        ctx.lineTo(path[i][1] * CELL + CELL / 2, path[i][0] * CELL + CELL / 2)
      }
      ctx.stroke()
    }

    // Start marker (green circle)
    ctx.fillStyle = '#00cc44'
    ctx.beginPath()
    ctx.arc(CELL / 2, CELL / 2, CELL * 0.8, 0, Math.PI * 2)
    ctx.fill()

    // Goal marker (red square)
    ctx.fillStyle = '#e03030'
    ctx.fillRect(49 * CELL, 49 * CELL, CELL, CELL)

  }, [configName, path, grid])

  const mu = Math.round(result.mutation_rate * 100)

  return (
    <div className="grid-panel">
      <div className="grid-title" style={{ borderColor: COLORS[configName] }}>
        <span className="grid-algo">{result.algorithm}</span>
        <span className="grid-mu">μ = {mu}%</span>
      </div>
      <canvas ref={canvasRef} width={SIZE} height={SIZE} className="grid-canvas" />
      <div className="grid-stats">
        <span>Fitness: <b>{result.avg_final_fitness.toFixed(1)}</b></span>
        <span>Collisions: <b>{result.avg_obstacle_collisions.toFixed(1)}</b></span>
        <span>Length: <b>{result.avg_path_length.toFixed(1)}</b></span>
      </div>
    </div>
  )
}

export default function PathGrid({ results, paths, grid }) {
  return (
    <div className="card">
      <h2 className="card-title">Best Paths on 50×50 Grid</h2>
      <p className="card-sub">
        <span className="legend-item"><span className="dot green" /> Start (0,0)</span>
        <span className="legend-item"><span className="dot red" /> Goal (49,49)</span>
        <span className="legend-item"><span className="dot dark" /> Obstacle</span>
      </p>
      <div className="grid-2x2">
        {results.map(r => (
          <GridCanvas
            key={r.config_name}
            configName={r.config_name}
            path={paths[r.config_name]}
            grid={grid}
            result={r}
          />
        ))}
      </div>
    </div>
  )
}
