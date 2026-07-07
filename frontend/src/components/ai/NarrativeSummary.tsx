interface NarrativeSummaryProps {
  narrative: string
  isLoading?: boolean
}

export default function NarrativeSummary({ narrative, isLoading = false }: NarrativeSummaryProps) {
  if (isLoading) {
    return (
      <div className="bg-gradient-to-r from-blue-50 to-indigo-50 rounded-xl p-5 border border-blue-100">
        <div className="flex items-center gap-2 mb-3">
          <span className="text-blue-500">✨</span>
          <span className="text-sm font-semibold text-blue-700">AI Data Narrative</span>
        </div>
        <div className="space-y-2">
          <div className="h-3 bg-blue-200 rounded animate-pulse w-full" />
          <div className="h-3 bg-blue-200 rounded animate-pulse w-4/5" />
          <div className="h-3 bg-blue-200 rounded animate-pulse w-3/5" />
        </div>
      </div>
    )
  }

  return (
    <div className="bg-gradient-to-r from-blue-50 to-indigo-50 rounded-xl p-5 border border-blue-100">
      <div className="flex items-center gap-2 mb-3">
        <span className="text-blue-500">✨</span>
        <span className="text-sm font-semibold text-blue-700">AI Data Narrative</span>
      </div>
      <p className="text-sm text-gray-700 leading-relaxed">{narrative || 'No narrative available.'}</p>
    </div>
  )
}
