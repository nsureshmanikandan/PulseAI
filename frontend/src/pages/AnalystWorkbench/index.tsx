import { useEffect, useState } from 'react'
import { useAppStore } from '../../store/useAppStore'
import FilterBar from '../../components/filters/FilterBar'
import PlotlyChart from '../../components/charts/PlotlyChart'
import DataGrid from '../../components/tables/DataGrid'

interface ChartConfig {
  data: object[]
  layout?: object
}

export function AnalystWorkbench() {
  const activeDataset = useAppStore((s) => s.activeDataset)
  const activeTab = useAppStore((s) => s.activeTab)
  const [columns, setColumns] = useState<string[]>([])
  const [chartType, setChartType] = useState('bar')
  const [chartConfig, setChartConfig] = useState<ChartConfig | null>(null)
  const [rowData] = useState<Record<string, unknown>[]>([])
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')

  // Load stats to get column names
  useEffect(() => {
    if (!activeDataset || !activeTab) return
    const id = activeDataset.id
    const tab = encodeURIComponent(activeTab)
    fetch(`/api/analytics/${id}/stats/${tab}`)
      .then((r) => r.json())
      .then((stats) => setColumns(Object.keys(stats)))
      .catch(console.error)
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
        body: JSON.stringify({
          tab_name: activeTab,
          chart_type: chartType,
          x: filters.x,
          y: filters.y,
        }),
      })
      if (!res.ok) {
        const err = await res.json()
        setError(err.detail || 'Chart generation failed')
        return
      }
      const config = await res.json()
      setChartConfig(config)
    } catch {
      setError('Failed to generate chart')
    } finally {
      setLoading(false)
    }
  }

  if (!activeDataset) {
    return (
      <div className="flex flex-col items-center justify-center h-full text-gray-400">
        <span className="text-5xl mb-4">🔬</span>
        <p className="text-lg font-medium">No dataset selected</p>
        <p className="text-sm mt-1">Upload a file or select a dataset from Data Sources</p>
      </div>
    )
  }

  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-2xl font-bold text-gray-900">Analyst Workbench</h2>
        <p className="text-sm text-gray-500 mt-1">{activeDataset.name} — {activeTab}</p>
      </div>

      <FilterBar
        columns={columns}
        onFilter={handleFilter}
        onChartTypeChange={setChartType}
        chartType={chartType}
      />

      {error && (
        <div className="bg-red-50 border border-red-200 text-red-700 rounded-lg px-4 py-3 text-sm">{error}</div>
      )}

      {loading && (
        <div className="bg-white rounded-xl border border-gray-200 h-64 flex items-center justify-center text-gray-400">
          Generating chart...
        </div>
      )}

      {chartConfig && !loading && (
        <div className="bg-white rounded-xl border border-gray-200 p-4">
          <PlotlyChart config={chartConfig} />
        </div>
      )}

      {rowData.length > 0 && (
        <div className="bg-white rounded-xl border border-gray-200 p-4">
          <h3 className="text-sm font-semibold text-gray-700 mb-3">Data Preview</h3>
          <DataGrid rowData={rowData} />
        </div>
      )}
    </div>
  )
}
