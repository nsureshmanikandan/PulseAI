interface Insight {
  type: string
  column: string
  message: string
  severity: 'info' | 'warning' | 'critical'
}

interface InsightCardProps {
  insight: Insight
}

const severityStyles = {
  info: 'bg-blue-50 border-blue-200 text-blue-800',
  warning: 'bg-yellow-50 border-yellow-200 text-yellow-800',
  critical: 'bg-red-50 border-red-200 text-red-800',
}

const severityIcon = {
  info: 'ℹ️',
  warning: '⚠️',
  critical: '🚨',
}

export default function InsightCard({ insight }: InsightCardProps) {
  const style = severityStyles[insight.severity] || severityStyles.info
  const icon = severityIcon[insight.severity] || 'ℹ️'

  return (
    <div className={`flex items-start gap-3 p-3 rounded-lg border ${style}`}>
      <span className="text-lg">{icon}</span>
      <div>
        <p className="text-sm font-medium">{insight.message}</p>
        <p className="text-xs mt-0.5 opacity-75">Column: {insight.column}</p>
      </div>
    </div>
  )
}
