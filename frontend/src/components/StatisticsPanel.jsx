const COLORS = {
  CGA_mut50:   '#1f77b4',
  CGA_mut80:   '#ff7f0e',
  RDIGA_mut50: '#2ca02c',
  RDIGA_mut80: '#d62728',
}
const LABELS = {
  CGA_mut50:   'CGA μ=50%',
  CGA_mut80:   'CGA μ=80%',
  RDIGA_mut50: 'RDIGA μ=50%',
  RDIGA_mut80: 'RDIGA μ=80%',
}
const ORDER = ['CGA_mut50', 'CGA_mut80', 'RDIGA_mut50', 'RDIGA_mut80']

const SVG_H = 300
const PAD_TOP = 20
const PAD_BOT = 48
const PAD_LEFT = 48
const BOX_W = 46
const SLOT_W = 130

function BoxplotSVG({ boxplots }) {
  const boxes = ORDER.map(name => ({ name, color: COLORS[name], s: boxplots[name] }))

  const allVals = boxes.flatMap(b => [b.s.min, b.s.max, ...b.s.outliers])
  const gMin = Math.min(...allVals)
  const gMax = Math.max(...allVals)
  const range = gMax - gMin || 1
  const plotH = SVG_H - PAD_TOP - PAD_BOT
  const SVG_W = PAD_LEFT + ORDER.length * SLOT_W + 20

  const sy = v => PAD_TOP + plotH - ((v - gMin) / range) * plotH

  const nTicks = 5
  const ticks = Array.from({ length: nTicks + 1 }, (_, i) => gMin + (range * i) / nTicks)

  return (
    <svg viewBox={`0 0 ${SVG_W} ${SVG_H}`} style={{ width: '100%', height: SVG_H }}>
      {/* Y-axis grid + labels */}
      {ticks.map((v, i) => (
        <g key={i}>
          <line
            x1={PAD_LEFT} y1={sy(v)} x2={SVG_W - 10} y2={sy(v)}
            stroke="#e2e8f0" strokeWidth={1}
          />
          <text x={PAD_LEFT - 6} y={sy(v) + 4} textAnchor="end" fontSize={10} fill="#94a3b8">
            {Math.round(v)}
          </text>
        </g>
      ))}

      {/* Y-axis label */}
      <text
        x={12} y={PAD_TOP + plotH / 2}
        textAnchor="middle" fontSize={11} fill="#718096"
        transform={`rotate(-90, 12, ${PAD_TOP + plotH / 2})`}
      >
        Final Fitness
      </text>

      {boxes.map((b, i) => {
        const cx = PAD_LEFT + i * SLOT_W + SLOT_W / 2
        const { s, color, name } = b

        return (
          <g key={name}>
            {/* dashed whisker lines */}
            <line x1={cx} y1={sy(s.min)} x2={cx} y2={sy(s.q1)}
                  stroke={color} strokeWidth={1.5} strokeDasharray="3,2" />
            <line x1={cx} y1={sy(s.q3)} x2={cx} y2={sy(s.max)}
                  stroke={color} strokeWidth={1.5} strokeDasharray="3,2" />
            {/* whisker caps */}
            <line x1={cx - 13} y1={sy(s.min)} x2={cx + 13} y2={sy(s.min)}
                  stroke={color} strokeWidth={2} />
            <line x1={cx - 13} y1={sy(s.max)} x2={cx + 13} y2={sy(s.max)}
                  stroke={color} strokeWidth={2} />
            {/* IQR box */}
            <rect
              x={cx - BOX_W / 2} y={sy(s.q3)}
              width={BOX_W} height={Math.max(sy(s.q1) - sy(s.q3), 1)}
              fill={color} fillOpacity={0.18} stroke={color} strokeWidth={2} rx={3}
            />
            {/* median */}
            <line
              x1={cx - BOX_W / 2} y1={sy(s.median)} x2={cx + BOX_W / 2} y2={sy(s.median)}
              stroke={color} strokeWidth={3}
            />
            {/* mean (diamond) */}
            <polygon
              points={`${cx},${sy(s.mean) - 5} ${cx + 5},${sy(s.mean)} ${cx},${sy(s.mean) + 5} ${cx - 5},${sy(s.mean)}`}
              fill={color} stroke="#fff" strokeWidth={1.2}
            />
            {/* outliers */}
            {s.outliers.map((v, oi) => (
              <circle key={oi} cx={cx} cy={sy(v)} r={3.5}
                      fill="none" stroke={color} strokeWidth={1.5} />
            ))}
            {/* x-axis label */}
            <text x={cx} y={SVG_H - PAD_BOT + 16} textAnchor="middle"
                  fontSize={11} fontWeight="600" fill={color}>
              {LABELS[name].split(' ')[0]}
            </text>
            <text x={cx} y={SVG_H - PAD_BOT + 30} textAnchor="middle"
                  fontSize={10} fill="#718096">
              {LABELS[name].split(' ').slice(1).join(' ')}
            </text>
          </g>
        )
      })}
    </svg>
  )
}

export default function StatisticsPanel({ stats }) {
  const { boxplots, tests } = stats

  return (
    <div className="card">
      <h2 className="card-title">Statistical Analysis</h2>
      <p className="card-sub">
        Final fitness distribution &nbsp;·&nbsp; Mann-Whitney U &nbsp;·&nbsp;
        Welch t-Test &nbsp;·&nbsp; Cohen's d &nbsp;&nbsp;(α = 0.05)
      </p>

      {/* Boxplot legend */}
      <div className="stat-legend">
        <span className="stat-legend-item">
          <svg width="22" height="10" style={{ verticalAlign: 'middle', marginRight: 4 }}>
            <line x1="0" y1="5" x2="22" y2="5" stroke="#555" strokeWidth="3" />
          </svg>
          Median
        </span>
        <span className="stat-legend-item">
          <svg width="12" height="12" style={{ verticalAlign: 'middle', marginRight: 4 }}>
            <polygon points="6,0 12,6 6,12 0,6" fill="#555" />
          </svg>
          Mean
        </span>
        <span className="stat-legend-item">
          <svg width="12" height="12" style={{ verticalAlign: 'middle', marginRight: 4 }}>
            <circle cx="6" cy="6" r="4" fill="none" stroke="#555" strokeWidth="1.5" />
          </svg>
          Outlier
        </span>
        <span className="stat-legend-item">
          <svg width="22" height="12" style={{ verticalAlign: 'middle', marginRight: 4 }}>
            <line x1="0" y1="6" x2="22" y2="6" stroke="#555" strokeWidth="1.5" strokeDasharray="3,2" />
          </svg>
          Whisker (1.5×IQR)
        </span>
      </div>

      <BoxplotSVG boxplots={boxplots} />

      {/* Statistical tests table */}
      <h3 className="stat-section-title">Hypothesis Tests</h3>
      <div className="table-wrap">
        <table className="cmp-table">
          <thead>
            <tr>
              <th>Comparison</th>
              <th>U</th>
              <th>Z</th>
              <th>p (MW)</th>
              <th>t</th>
              <th>p (t)</th>
              <th>d</th>
              <th>Effect</th>
              <th>Sig.</th>
            </tr>
          </thead>
          <tbody>
            {tests.map(t => (
              <tr key={t.label} className={t.significant ? 'best-row' : ''}>
                <td>
                  <span className="config-dot" style={{ background: COLORS[t.name_a] }} />
                  <span className="config-dot" style={{ background: COLORS[t.name_b] }} />
                  {t.label}
                </td>
                <td>{t.mw_u.toFixed(0)}</td>
                <td>{t.mw_z.toFixed(3)}</td>
                <td className={t.mw_p < 0.05 ? 'best-cell' : ''}>{t.mw_p.toFixed(4)}</td>
                <td>{t.t_stat.toFixed(3)}</td>
                <td className={t.t_p < 0.05 ? 'best-cell' : ''}>{t.t_p.toFixed(4)}</td>
                <td>{t.cohens_d.toFixed(3)}</td>
                <td>
                  <span className={`effect-badge effect-${t.effect}`}>{t.effect}</span>
                </td>
                <td>
                  {t.significant
                    ? <span className="sig-star">*</span>
                    : <span className="ns-label">n.s.</span>}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  )
}
