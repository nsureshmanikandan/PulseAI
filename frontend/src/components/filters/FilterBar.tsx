import { useState, useEffect } from 'react'

interface FilterBarProps {
  columns: string[]
  onFilter: (filters: Record<string, string>) => void
  onChartTypeChange: (type: string) => void
  chartType: string
}

const CHART_TYPES = [
  { value: 'bar', label: 'Bar' },
  { value: 'line', label: 'Line' },
  { value: 'scatter', label: 'Scatter' },
  { value: 'pie', label: 'Pie (donut)' },
  { value: 'histogram', label: 'Histogram' },
  { value: 'heatmap', label: 'Correlation Heatmap' },
]

const sel: React.CSSProperties = {
  background: 'rgba(255,255,255,0.06)',
  border: '1px solid rgba(255,255,255,0.12)',
  color: '#e2e8f0',
  borderRadius: '10px',
  padding: '7px 10px',
  fontSize: '13px',
  outline: 'none',
  minWidth: '150px',
  cursor: 'pointer',
}

export default function FilterBar({ columns, onFilter, onChartTypeChange, chartType }: FilterBarProps) {
  const [xCol, setXCol] = useState('')
  const [yCol, setYCol] = useState('')

  useEffect(() => {
    if (columns.length > 0) {
      setXCol((p) => (p && columns.includes(p) ? p : columns[0]))
      setYCol((p) => (p && columns.includes(p) ? p : (columns[1] ?? columns[0])))
    }
  }, [columns])

  const noY = chartType === 'histogram' || chartType === 'heatmap'

  return (
    <div className="rounded-2xl p-4 flex flex-wrap items-end gap-4"
      style={{ background: 'rgba(255,255,255,0.04)', border: '1px solid rgba(255,255,255,0.08)' }}>

      <div className="flex flex-col gap-1.5">
        <label className="text-xs font-semibold text-gray-400 uppercase tracking-widest">Chart Type</label>
        <select value={chartType} onChange={(e) => onChartTypeChange(e.target.value)} style={sel}>
          {CHART_TYPES.map(({ value, label }) => (
            <option key={value} value={value} style={{ background: '#1e293b' }}>{label}</option>
          ))}
        </select>
      </div>

      <div className="flex flex-col gap-1.5">
        <label className="text-xs font-semibold text-gray-400 uppercase tracking-widest">
          {chartType === 'pie' ? 'Category' : chartType === 'histogram' ? 'Column' : 'X Axis'}
        </label>
        <select value={xCol} onChange={(e) => setXCol(e.target.value)} style={sel} disabled={!columns.length}>
          {columns.length === 0
            ? <option>Loading columns…</option>
            : columns.map((c) => <option key={c} value={c} style={{ background: '#1e293b' }}>{c}</option>)}
        </select>
      </div>

      {!noY && (
        <div className="flex flex-col gap-1.5">
          <label className="text-xs font-semibold text-gray-400 uppercase tracking-widest">Y Axis</label>
          <select value={yCol} onChange={(e) => setYCol(e.target.value)} style={sel} disabled={!columns.length}>
            {columns.map((c) => <option key={c} value={c} style={{ background: '#1e293b' }}>{c}</option>)}
          </select>
        </div>
      )}

      <button
        onClick={() => onFilter({ x: xCol, y: yCol })}
        disabled={!columns.length || !xCol}
        className="px-5 py-2 bg-blue-600 hover:bg-blue-500 text-white text-sm font-semibold rounded-xl transition-colors disabled:opacity-40 disabled:cursor-not-allowed"
      >
        Generate Chart
      </button>
    </div>
  )
}
