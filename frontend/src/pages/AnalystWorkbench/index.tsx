import { useEffect, useState } from 'react'
import { useAppStore } from '../../store/useAppStore'
import { useHealActiveTab } from '../../hooks/useHealActiveTab'
import FilterBar from '../../components/filters/FilterBar'
import PlotlyChart from '../../components/charts/PlotlyChart'

interface ChartConfig {
  data: object[]
  layout?: object
}

export function AnalystWorkbench() {
  useHealActiveTab()
  const activeDataset = useAppStore((s) => s.activeDataset)
  const activeTab = useAppStore((s) => s.activeTab)
  const [columns, setColumns] = useState<string[]>([])
  const [chartType, setChartType] = useState('bar')
  const [chartConfig, setChartConfig] = useState<ChartConfig | null>(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')

  useEffect(() => {
    if (!activeDataset || !activeTab) return
    setColumns([])
    setChartConfig(null)
    const id = activeDataset.id
    const tab = encodeURIComponent(activeTab)
    fetch(`/api/analytics/${id}/stats/${tab}`)
      .then((r) => r.json())
      .then((stats) => setColumns(Object.keys(stats)))
      .catch(() => setError('Failed to load dataset columns'))
  }, [activeDataset, activeTab])

  const handleFilter = async (filters: Record<string, string>) => {
    if (!activeDataset || !activeTab) return
    setLoading(true)
    setError('')
    try {
      const id = activeDataset.id
      const res = await fetch(`/api/analytics/${id}/chart`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ tab_name: activeTab, chart_type: chartType, x: filters.x, y: filters.y }),
      })
      if (!res.ok) {
        const err = await res.json()
        setError(err.detail || 'Chart generation failed')
        return
      }
      setChartConfig(await res.json())
    } catch {
      setError('Failed to generate chart')
    } finally {
      setLoading(false)
    }
  }

  if (!activeDataset) {
    return (
      <div className="flex flex-col items-center justify-center h-full gap-3">
        <div className="w-16 h-16 rounded-2xl bg-blue-500/10 border border-blue-500/20 flex items-center justify-center text-3xl">🔬</div>
        <p className="text-lg font-semibold text-gray-200">No dataset selected</p>
        <p className="text-sm text-gray-500">Go to Data Sources and select a dataset</p>
      </div>
    )
  }

  return (
    <div className="space-y-5">
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-xl font-bold text-white">Analyst Workbench</h2>
          <p className="text-xs text-gray-400 mt-1">{activeDataset.name} · {activeTab}</p>
        </div>
        <span className="text-xs bg-purple-500/10 border border-purple-500/20 text-purple-400 px-3 py-1 rounded-full font-medium">
          Analyst View
        </span>
      </div>

      <FilterBar
        columns={columns}
        onFilter={handleFilter}
        onChartTypeChange={setChartType}
        chartType={chartType}
      />

      {error && (
        <div className="bg-red-500/10 border border-red-500/20 text-red-400 rounded-xl px-4 py-3 text-sm">
          {error}
        </div>
      )}

      {loading && (
        <div className="rounded-2xl border flex items-center justify-center h-64 text-gray-500 text-sm"
          style={{ background: 'rgba(255,255,255,0.03)', borderColor: 'rgba(255,255,255,0.08)' }}>
          <div className="flex flex-col items-center gap-3">
            <div className="w-6 h-6 border-2 border-blue-500 border-t-transparent rounded-full animate-spin" />
            Generating chart…
          </div>
        </div>
      )}

      {chartConfig && !loading && (
        <div className="rounded-2xl border p-4"
          style={{ background: 'rgba(255,255,255,0.03)', borderColor: 'rgba(255,255,255,0.08)' }}>
          <PlotlyChart config={chartConfig} />
        </div>
      )}

      {!chartConfig && !loading && !error && (
        <div className="rounded-2xl border flex items-center justify-center h-48 text-gray-600 text-sm"
          style={{ borderStyle: 'dashed', borderColor: 'rgba(255,255,255,0.08)' }}>
          Select axes and click Generate Chart
        </div>
      )}
    </div>
  )
}
