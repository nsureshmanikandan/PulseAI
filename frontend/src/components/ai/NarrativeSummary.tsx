import ReactMarkdown from 'react-markdown'

interface NarrativeSummaryProps {
  narrative: string
  isLoading?: boolean
}

export default function NarrativeSummary({ narrative, isLoading = false }: NarrativeSummaryProps) {
  return (
    <div className="rounded-2xl p-5 border" style={{ background: 'rgba(59,130,246,0.06)', borderColor: 'rgba(59,130,246,0.2)' }}>
      <div className="flex items-center gap-2 mb-3">
        <span className="text-base">✨</span>
        <span className="text-sm font-semibold text-blue-400">AI Data Narrative</span>
      </div>

      {isLoading ? (
        <div className="space-y-2">
          {[100, 80, 60].map((w, i) => (
            <div key={i} className="h-3 rounded animate-pulse" style={{ width: `${w}%`, background: 'rgba(59,130,246,0.15)' }} />
          ))}
        </div>
      ) : narrative ? (
        <div className="text-sm text-gray-300 leading-relaxed prose-sm">
          <ReactMarkdown
            components={{
              p: ({ children }) => <p className="mb-2 last:mb-0 text-gray-300">{children}</p>,
              strong: ({ children }) => <strong className="font-semibold text-white">{children}</strong>,
              ul: ({ children }) => <ul className="list-disc list-inside space-y-1 mb-2 text-gray-300">{children}</ul>,
              li: ({ children }) => <li>{children}</li>,
            }}
          >
            {narrative}
          </ReactMarkdown>
        </div>
      ) : (
        <p className="text-sm text-gray-500 italic">Narrative will appear after dataset analysis completes.</p>
      )}
    </div>
  )
}
