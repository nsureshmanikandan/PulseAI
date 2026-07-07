import { useEffect, useState } from 'react'
import { useAppStore } from '../../store/useAppStore'
import NarrativeSummary from '../../components/ai/NarrativeSummary'
import InsightCard from '../../components/ai/InsightCard'

interface KPI {
  column: string
  sum: number
  mean: number
  min: number
  max: number
  count: number
}

interface Insight {
  type: string
  column: string
  message: string
  severity: 'info' | 'warning' | 'critical'
}

export function ExecutiveDashboard() {
  const activeDataset = useAppStore((s) => s.activeDataset)
  const activeTab = useAppStore((s) => s.activeTab)
  const [kpis, setKpis] = useState<KPI[]>([])
  const [insights, setInsights] = useState<Insight[]>([])
  const [narrative, setNarrative] = useState('')
  const [loading, setLoading] = useState(false)

  useEffect(() => {
    if (!activeDataset || !activeTab) return
    setLoading(true)

    const base = `/api`
    const id = activeDataset.id
    const tab = encodeURIComponent(activeTab)

    Promise.all([
      fetch(`${base}/analytics/${id}/kpis/${tab}`).then((r) => r.json()),
      fetch(`${base}/ai/${id}/insights/${tab}`).then((r) => r.json()),
      fetch(`${base}/ai/${id}/narrative/${tab}`).then((r) => r.json()),
    ])
      .then(([kpiData, insightData, narrativeData]) => {
        setKpis(Array.isArray(kpiData) ? kpiData : [])
        setInsights(Array.isArray(insightData) ? insightData : [])
        setNarrative(narrativeData?.narrative || '')
      })
      .catch(console.error)
      .finally(() => setLoading(false))
  }, [activeDataset, activeTab])

  if (!activeDataset) {
    return (
      <div className="flex flex-col items-center justify-center h-full text-gray-400">
        <span className="text-5xl mb-4">📊</span>
        <p className="text-lg font-medium">No dataset selected</p>
        <p className="text-sm mt-1">Upload a file or select a dataset from Data Sources</p>
      </div>
    )
  }

  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-2xl font-bold text-gray-900">{activeDataset.name}</h2>
        <p className="text-sm text-gray-500 mt-1">Executive Summary — {activeTab}</p>
      </div>

      {/* KPI Cards */}
      <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-4">
        {kpis.map((kpi) => (
          <div key={kpi.column} className="bg-white rounded-xl border border-gray-200 p-4 shadow-sm">
            <p className="text-xs text-gray-500 uppercase tracking-wide">{kpi.column}</p>
            <p className="text-2xl font-bold text-gray-900 mt-1">
              {kpi.sum.toLocaleString(undefined, { maximumFractionDigits: 0 })}
            </p>
            <p className="text-xs text-gray-400 mt-1">avg {kpi.mean.toLocaleString(undefined, { maximumFractionDigits: 1 })}</p>
          </div>
        ))}
        {loading && !kpis.length &&
          Array.from({ length: 4 }).map((_, i) => (
            <div key={i} className="bg-white rounded-xl border border-gray-200 p-4 shadow-sm animate-pulse">
              <div className="h-3 bg-gray-200 rounded w-2/3 mb-2" />
              <div className="h-7 bg-gray-200 rounded w-1/2" />
            </div>
          ))
        }
      </div>

      {/* AI Narrative */}
      <NarrativeSummary narrative={narrative} isLoading={loading && !narrative} />

      {/* Insights */}
      {insights.length > 0 && (
        <div>
          <h3 className="text-sm font-semibold text-gray-700 mb-3">Auto-detected Insights</h3>
          <div className="space-y-2">
            {insights.map((insight, i) => (
              <InsightCard key={i} insight={insight} />
            ))}
          </div>
        </div>
      )}
    </div>
  )
}

export default ExecutiveDashboard
