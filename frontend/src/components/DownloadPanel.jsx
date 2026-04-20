const CELL = 7
const COLORS = {
  CGA_mut50: '#1f77b4', CGA_mut80: '#ff7f0e',
  RDIGA_mut50: '#2ca02c', RDIGA_mut80: '#d62728',
}

function triggerDownload(url, filename) {
  const a = document.createElement('a')
  a.href = url
  a.download = filename
  a.click()
}

function downloadJSON(results) {
  const blob = new Blob([JSON.stringify(results, null, 2)], { type: 'application/json' })
  triggerDownload(URL.createObjectURL(blob), 'results.json')
}

function downloadCSV(results) {
  const headers = [
    'Config', 'Algorithm', 'Mutation Rate',
    'Avg Fitness', 'Std Fitness',
    'Avg Collisions', 'Avg Path Length', 'Avg Runtime (s)',
  ]
  const rows = results.map(r => [
    r.config_name,
    r.algorithm,
    r.mutation_rate,
    r.avg_final_fitness.toFixed(2),
    r.std_final_fitness.toFixed(2),
    r.avg_obstacle_collisions.toFixed(1),
    r.avg_path_length.toFixed(1),
    r.avg_runtime_seconds.toFixed(2),
  ])
  const csv = [headers, ...rows].map(row => row.join(',')).join('\n')
  const blob = new Blob([csv], { type: 'text/csv' })
  triggerDownload(URL.createObjectURL(blob), 'results.csv')
}

function downloadPathGridsPNG(grid, paths, results) {
  const PAD     = 12
  const LABEL_H = 42
  const gridPx  = 50 * CELL   // 350px per grid

  const W = 2 * gridPx + 3 * PAD
  const H = 2 * (gridPx + LABEL_H) + 3 * PAD

  const canvas = document.createElement('canvas')
  canvas.width  = W
  canvas.height = H
  const ctx = canvas.getContext('2d')

  // Background
  ctx.fillStyle = '#f0f2f5'
  ctx.fillRect(0, 0, W, H)

  results.forEach((r, idx) => {
    const col = idx % 2
    const row = Math.floor(idx / 2)
    const ox  = PAD + col * (gridPx + PAD)
    const oy  = PAD + row * (gridPx + LABEL_H + PAD)

    // Label
    ctx.fillStyle = COLORS[r.config_name]
    ctx.font = 'bold 12px Segoe UI, sans-serif'
    ctx.fillText(
      `${r.algorithm}  μ=${Math.round(r.mutation_rate * 100)}%  |  Fitness: ${r.avg_final_fitness.toFixed(1)}`,
      ox, oy + 15
    )
    ctx.fillStyle = '#718096'
    ctx.font = '10px Segoe UI, sans-serif'
    ctx.fillText(
      `Collisions: ${r.avg_obstacle_collisions.toFixed(1)}   Path length: ${r.avg_path_length.toFixed(1)}`,
      ox, oy + 30
    )

    const gy = oy + LABEL_H

    // Grid cells
    for (let gr = 0; gr < 50; gr++) {
      for (let gc = 0; gc < 50; gc++) {
        ctx.fillStyle = grid[gr][gc] === 1 ? '#4a4a4a' : '#ebebeb'
        ctx.fillRect(ox + gc * CELL, gy + gr * CELL, CELL, CELL)
      }
    }

    // Path
    const path = paths[r.config_name]
    if (path?.length > 1) {
      ctx.strokeStyle = COLORS[r.config_name]
      ctx.lineWidth   = 2.0
      ctx.lineJoin    = 'round'
      ctx.beginPath()
      ctx.moveTo(ox + path[0][1] * CELL + CELL / 2, gy + path[0][0] * CELL + CELL / 2)
      path.slice(1).forEach(([pr, pc]) =>
        ctx.lineTo(ox + pc * CELL + CELL / 2, gy + pr * CELL + CELL / 2)
      )
      ctx.stroke()
    }

    // Start (green circle)
    ctx.fillStyle = '#00cc44'
    ctx.beginPath()
    ctx.arc(ox + CELL / 2, gy + CELL / 2, CELL * 0.75, 0, Math.PI * 2)
    ctx.fill()

    // Goal (red square)
    ctx.fillStyle = '#e03030'
    ctx.fillRect(ox + 49 * CELL, gy + 49 * CELL, CELL, CELL)
  })

  triggerDownload(canvas.toDataURL('image/png'), 'best_paths.png')
}

function downloadFitnessCurvesPNG() {
  const container = document.getElementById('fitness-chart-container')
  const svgEl     = container?.querySelector('svg')
  if (!svgEl) { alert('Chart not rendered yet.'); return }

  const svgStr  = new XMLSerializer().serializeToString(svgEl)
  const svgBlob = new Blob([svgStr], { type: 'image/svg+xml;charset=utf-8' })
  const url     = URL.createObjectURL(svgBlob)

  const img = new Image()
  img.onload = () => {
    const canvas = document.createElement('canvas')
    // 2× resolution for crisp PNG
    canvas.width  = svgEl.clientWidth  * 2
    canvas.height = svgEl.clientHeight * 2
    const ctx = canvas.getContext('2d')
    ctx.fillStyle = '#ffffff'
    ctx.fillRect(0, 0, canvas.width, canvas.height)
    ctx.scale(2, 2)
    ctx.drawImage(img, 0, 0)
    URL.revokeObjectURL(url)
    triggerDownload(canvas.toDataURL('image/png'), 'fitness_curves.png')
  }
  img.src = url
}

export default function DownloadPanel({ results, paths, grid }) {
  return (
    <div className="card download-panel">
      <h2 className="card-title">Download Results</h2>
      <div className="dl-buttons">
        <button className="dl-btn json"  onClick={() => downloadJSON(results)}>
          <span className="dl-icon">⬇</span> results.json
        </button>
        <button className="dl-btn csv"   onClick={() => downloadCSV(results)}>
          <span className="dl-icon">⬇</span> results.csv
        </button>
        <button className="dl-btn chart" onClick={downloadFitnessCurvesPNG}>
          <span className="dl-icon">⬇</span> fitness_curves.png
        </button>
        <button className="dl-btn grid"  onClick={() => downloadPathGridsPNG(grid, paths, results)}>
          <span className="dl-icon">⬇</span> best_paths.png
        </button>
      </div>
    </div>
  )
}
