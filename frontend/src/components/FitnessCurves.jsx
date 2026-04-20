import {
  LineChart, Line, XAxis, YAxis, CartesianGrid,
  Tooltip, Legend, ResponsiveContainer, ReferenceLine,
} from 'recharts'

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

export default function FitnessCurves({ results }) {
  // Build recharts data: [{gen, CGA_mut50, CGA_mut80, ...}, ...]
  const n = results[0].avg_fitness_curve.length
  const data = Array.from({ length: n }, (_, i) => {
    const row = { gen: i + 1 }
    results.forEach(r => { row[r.config_name] = Math.round(r.avg_fitness_curve[i]) })
    return row
  })

  const allVals = results.flatMap(r => r.avg_fitness_curve)
  const yMin = Math.floor(Math.min(...allVals) * 0.97)
  const yMax = Math.ceil(Math.max(...allVals)  * 1.01)

  return (
    <div className="card" id="fitness-chart-container">
      <h2 className="card-title">Fitness Convergence</h2>
      <p className="card-sub">Average best fitness per generation (lower = better)</p>
      <ResponsiveContainer width="100%" height={340}>
        <LineChart data={data} margin={{ top: 8, right: 30, bottom: 8, left: 10 }}>
          <CartesianGrid strokeDasharray="3 3" opacity={0.3} />
          <XAxis
            dataKey="gen"
            label={{ value: 'Generation', position: 'insideBottom', offset: -2, fontSize: 12 }}
            tick={{ fontSize: 11 }}
          />
          <YAxis
            domain={[yMin, yMax]}
            label={{ value: 'Avg Best Fitness', angle: -90, position: 'insideLeft', fontSize: 12 }}
            tick={{ fontSize: 11 }}
          />
          <Tooltip
            formatter={(val, name) => [val.toLocaleString(), LABELS[name] ?? name]}
            labelFormatter={gen => `Generation ${gen}`}
          />
          <Legend
            formatter={name => LABELS[name] ?? name}
            wrapperStyle={{ fontSize: 12 }}
          />
          {results.map((r, i) => (
            <Line
              key={r.config_name}
              type="monotone"
              dataKey={r.config_name}
              stroke={COLORS[r.config_name]}
              strokeWidth={2.5}
              dot={false}
              activeDot={{ r: 5, strokeWidth: 2 }}
              isAnimationActive={true}
              animationDuration={1200}
              animationEasing="ease-out"
              animationBegin={i * 200}
            />
          ))}
        </LineChart>
      </ResponsiveContainer>
    </div>
  )
}
