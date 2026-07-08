import { useEffect, useState } from 'react'
import { useAppStore } from '../../store/useAppStore'
import { useHealActiveTab } from '../../hooks/useHealActiveTab'
import NarrativeSummary from '../../components/ai/NarrativeSummary'
import InsightCard from '../../components/ai/InsightCard'
import PlotlyChart from '../../components/charts/PlotlyChart'

interface KPI {
  id: string
  label: string
  value: string
  raw: number
  subtitle: string
  type: 'rate' | 'currency' | 'score' | 'days' | 'count' | 'numeric'
  color: 'red' | 'green' | 'blue' | 'yellow' | 'purple'
}
interface Insight { type: string; column: string; message: string; severity: 'info' | 'warning' | 'critical' }
interface AutoChart { title: string; subtitle: string; data: object[]; layout: object }

const COLOR_MAP: Record<string, { text: string; bg: string; border: string; icon: string }> = {
  red:    { text: '#f87171', bg: 'rgba(239,68,68,0.10)',   border: 'rgba(239,68,68,0.25)',   icon: '⚠️' },
  green:  { text: '#34d399', bg: 'rgba(16,185,129,0.10)',  border: 'rgba(16,185,129,0.25)',  icon: '✅' },
  blue:   { text: '#60a5fa', bg: 'rgba(59,130,246,0.10)',  border: 'rgba(59,130,246,0.25)',  icon: '📊' },
  yellow: { text: '#fbbf24', bg: 'rgba(245,158,11,0.10)',  border: 'rgba(245,158,11,0.25)',  icon: '⏱️' },
  purple: { text: '#a78bfa', bg: 'rgba(139,92,246,0.10)',  border: 'rgba(139,92,246,0.25)',  icon: '🎯' },
}

const TYPE_ICON: Record<string, string> = {
  rate: '📈', currency: '💰', score: '🎯', days: '⏱️', count: '🔢', numeric: '📊',
}

function KPICard({ kpi }: { kpi: KPI }) {
  const c = COLOR_MAP[kpi.color] ?? COLOR_MAP.blue
  return (
    <div className="rounded-2xl p-4 border transition-all hover:scale-[1.01]"
      style={{ background: c.bg, borderColor: c.border }}>
      <div className="flex items-center justify-between mb-2">
        <span className="text-base">{TYPE_ICON[kpi.type] ?? '📊'}</span>
        <span className="text-xs px-2 py-0.5 rounded-full font-semibold uppercase tracking-wide"
          style={{ background: 'rgba(0,0,0,0.25)', color: c.text }}>
          {kpi.type}
        </span>
      </div>
      <p className="text-xs font-semibold uppercase tracking-widest mb-1 truncate"
        style={{ color: c.text }}>{kpi.label}</p>
      <p className="text-2xl font-bold text-white tabular-nums leading-tight">{kpi.value}</p>
      <p className="text-xs mt-1.5 truncate" style={{ color: 'rgba(255,255,255,0.4)' }}>{kpi.subtitle}</p>
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
            : kpis.map((kpi) => <KPICard key={kpi.id} kpi={kpi} />)
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
