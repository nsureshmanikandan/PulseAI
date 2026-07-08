interface Insight {
  type: string
  column: string
  message: string
  severity: 'info' | 'warning' | 'critical'
}

const severityConfig = {
  info:     { border: 'rgba(59,130,246,0.25)',  bg: 'rgba(59,130,246,0.08)',  text: '#93c5fd', icon: 'ℹ️' },
  warning:  { border: 'rgba(234,179,8,0.25)',   bg: 'rgba(234,179,8,0.08)',   text: '#fde047', icon: '⚠️' },
  critical: { border: 'rgba(239,68,68,0.25)',   bg: 'rgba(239,68,68,0.08)',   text: '#fca5a5', icon: '🚨' },
}

export default function InsightCard({ insight }: { insight: Insight }) {
  const cfg = severityConfig[insight.severity] ?? severityConfig.info
  return (
    <div className="flex items-start gap-3 p-3.5 rounded-xl border"
      style={{ background: cfg.bg, borderColor: cfg.border }}>
      <span className="text-base mt-0.5">{cfg.icon}</span>
      <div>
        <p className="text-sm font-medium" style={{ color: cfg.text }}>{insight.message}</p>
        <p className="text-xs mt-0.5 text-gray-500">Column: {insight.column}</p>
      </div>
    </div>
  )
}
