import { useEffect, useState } from 'react'
import { useAppStore } from '../../store/useAppStore'
import { useHealActiveTab } from '../../hooks/useHealActiveTab'
import NarrativeSummary from '../../components/ai/NarrativeSummary'
import InsightCard from '../../components/ai/InsightCard'
import PlotlyChart from '../../components/charts/PlotlyChart'

interface KPI { column: string; sum: number; mean: number; min: number; max: number }
interface Insight { type: string; column: string; message: string; severity: 'info' | 'warning' | 'critical' }
interface AutoChart { title: string; subtitle: string; data: object[]; layout: object }

function KPICard({ kpi }: { kpi: KPI }) {
  return (
    <div className="rounded-2xl p-5 border hover:border-blue-500/30 transition-colors"
      style={{ background: 'rgba(255,255,255,0.05)', borderColor: 'rgba(255,255,255,0.09)' }}>
      <p className="text-xs text-gray-400 uppercase tracking-widest font-semibold truncate">{kpi.column}</p>
      <p className="text-3xl font-bold text-white mt-2 tabular-nums">
        {kpi.sum.toLocaleString(undefined, { maximumFractionDigits: 0 })}
      </p>
      <div className="flex gap-3 mt-2.5 text-xs text-gray-500">
        <span>Avg <span className="text-gray-300 font-medium">{kpi.mean.toLocaleString(undefined, { maximumFractionDigits: 1 })}</span></span>
        <span>Min <span className="text-gray-300 font-medium">{kpi.min.toLocaleString(undefined, { maximumFractionDigits: 0 })}</span></span>
        <span>Max <span className="text-gray-300 font-medium">{kpi.max.toLocaleString(undefined, { maximumFractionDigits: 0 })}</span></span>
      </div>
    </div>
  )
}

function ChartCard({ chart }: { chart: AutoChart }) {
  return (
    <div className="rounded-2xl border overflow-hidden"
      style={{ background: 'rgba(255,255,255,0.03)', borderColor: 'rgba(255,255,255,0.08)' }}>
      <div className="px-4 pt-4 pb-2">
        <p className="text-sm font-semibold text-gray-200">{chart.title}</p>
        <p className="text-xs text-gray-500 mt-0.5">{chart.subtitle}</p>
      </div>
      <PlotlyChart config={{ data: chart.data, layout: chart.layout }} />
    </div>
  )
}

function Skeleton({ className = '' }: { className?: string }) {
  return <div className={`rounded-2xl shimmer ${className}`} style={{ borderRadius: '16px' }} />
}

export function ExecutiveDashboard() {
  useHealActiveTab()
  const activeDataset = useAppStore((s) => s.activeDataset)
  const activeTab = useAppStore((s) => s.activeTab)
  const [kpis, setKpis] = useState<KPI[]>([])
  const [insights, setInsights] = useState<Insight[]>([])
  const [narrative, setNarrative] = useState('')
  const [autoCharts, setAutoCharts] = useState<AutoChart[]>([])
  const [loading, setLoading] = useState(false)
  const [chartsLoading, setChartsLoading] = useState(false)

  useEffect(() => {
    if (!activeDataset || !activeTab) return
    setLoading(true)
    setChartsLoading(true)
    setKpis([]); setInsights([]); setNarrative(''); setAutoCharts([])

    const id = activeDataset.id
    const tab = encodeURIComponent(activeTab)

    // KPIs + narrative + insights in parallel
    Promise.all([
      fetch(`/api/analytics/${id}/kpis/${tab}`).then((r) => r.json()).catch(() => []),
      fetch(`/api/ai/${id}/insights/${tab}`).then((r) => r.json()).catch(() => []),
      fetch(`/api/ai/${id}/narrative/${tab}`).then((r) => r.json()).catch(() => ({})),
    ]).then(([kpiData, insightData, narrativeData]) => {
      setKpis(Array.isArray(kpiData) ? kpiData : [])
      setInsights(Array.isArray(insightData) ? insightData : [])
      setNarrative(narrativeData?.narrative || '')
    }).finally(() => setLoading(false))

    // Auto-charts separately (can be slow)
    fetch(`/api/analytics/${id}/auto-charts/${tab}`)
      .then((r) => r.json())
      .then((data) => setAutoCharts(Array.isArray(data) ? data : []))
      .catch(() => {})
      .finally(() => setChartsLoading(false))

  }, [activeDataset, activeTab])

  if (!activeDataset) {
    return (
      <div className="flex flex-col items-center justify-center h-full gap-3">
        <div className="w-16 h-16 rounded-2xl bg-blue-500/10 border border-blue-500/20 flex items-center justify-center text-3xl">📊</div>
        <p className="text-lg font-semibold text-gray-200">No dataset selected</p>
        <p className="text-sm text-gray-500">Go to Data Sources and select a dataset</p>
      </div>
    )
  }

  const isAnyLoading = loading || chartsLoading

  return (
    <div className="space-y-7">
      {/* Top progress bar */}
      {isAnyLoading && (
        <div className="progress-bar-track">
          <div className="progress-bar-fill" />
        </div>
      )}

      {/* Header */}
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-3">
          <div>
            <h2 className="text-xl font-bold text-white">{activeDataset.name}</h2>
            {isAnyLoading && (
              <div className="flex items-center gap-2 mt-1">
                <div className="flex gap-0.5">
                  {[0,1,2].map(i => (
                    <span key={i} className="w-1.5 h-1.5 rounded-full bg-blue-400"
                      style={{ animation: `progress-glow 1.2s ease-in-out ${i * 0.2}s infinite` }} />
                  ))}
                </div>
                <span className="text-xs text-blue-400 font-medium">
                  {loading ? 'Loading metrics…' : 'Generating charts…'}
                </span>
              </div>
            )}
            <p className="text-xs text-gray-400 mt-1">Executive Summary · {activeTab}</p>
          </div>
        </div>
        <span className="text-xs bg-blue-500/10 border border-blue-500/20 text-blue-400 px-3 py-1 rounded-full font-semibold">
          Executive View
        </span>
      </div>

      {/* KPI Cards */}
      <section>
        <p className="text-xs text-gray-500 uppercase tracking-widest font-semibold mb-3">Key Metrics</p>
        <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-3">
          {loading && !kpis.length
            ? Array.from({ length: 4 }).map((_, i) => <Skeleton key={i} className="h-28" />)
            : kpis.map((kpi) => <KPICard key={kpi.column} kpi={kpi} />)
          }
        </div>
      </section>

      {/* AI Narrative */}
      <NarrativeSummary narrative={narrative} isLoading={loading && !narrative} />

      {/* Auto-generated charts */}
      <section>
        <p className="text-xs text-gray-500 uppercase tracking-widest font-semibold mb-3">Data Visualisations</p>

        {chartsLoading && autoCharts.length === 0 ? (
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
            {Array.from({ length: 4 }).map((_, i) => <Skeleton key={i} className="h-72" />)}
          </div>
        ) : autoCharts.length > 0 ? (
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
            {autoCharts.map((chart, i) => <ChartCard key={i} chart={chart} />)}
          </div>
        ) : !chartsLoading ? (
          <div className="rounded-2xl border flex items-center justify-center h-32 text-gray-600 text-sm"
            style={{ borderStyle: 'dashed', borderColor: 'rgba(255,255,255,0.08)' }}>
            No visualisations available for this dataset.
          </div>
        ) : null}
      </section>

      {/* Insights */}
      {insights.length > 0 && (
        <section>
          <p className="text-xs text-gray-500 uppercase tracking-widest font-semibold mb-3">Auto-detected Insights</p>
          <div className="space-y-2">
            {insights.map((insight, i) => <InsightCard key={i} insight={insight} />)}
          </div>
        </section>
      )}
    </div>
  )
}

export default ExecutiveDashboard
