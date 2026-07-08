import { useState, useRef, useEffect } from 'react'
import ReactMarkdown from 'react-markdown'
import remarkGfm from 'remark-gfm'
import { useAppStore } from '../../store/useAppStore'
import { useWebSocket } from '../../hooks/useWebSocket'

interface Message {
  id: string
  role: 'user' | 'assistant'
  content: string
  isError?: boolean
}

const FALLBACK_SUGGESTIONS = [
  'What are the top 5 categories by count?',
  'Show me a summary of all numeric columns',
  'What is the total and average of each numeric field?',
  'Are there any missing values?',
  'Which rows have the highest values?',
  'What are the outliers in this dataset?',
  'Show me the distribution of values',
  'Is there any correlation between columns?',
  'Give me a complete statistical summary',
  'What insights can you find in this data?',
]

const CATEGORY_ICONS: Record<number, string> = {
  0: '📊', 1: '🏆', 2: '🔗', 3: '📈', 4: '🔍',
  5: '⚠️', 6: '📋', 7: '🧮', 8: '💡', 9: '🎯',
}

export function AIChat() {
  const activeDataset = useAppStore((s) => s.activeDataset)
  const activeTab = useAppStore((s) => s.activeTab)
  const [messages, setMessages] = useState<Message[]>([])
  const [input, setInput] = useState('')
  const [isWaiting, setIsWaiting] = useState(false)
  const [suggestions, setSuggestions] = useState<string[]>([])
  const [suggestionsLoading, setSuggestionsLoading] = useState(false)
  const bottomRef = useRef<HTMLDivElement>(null)
  const textareaRef = useRef<HTMLTextAreaElement>(null)

  const { connected, error: wsError, send } = useWebSocket({
    datasetId: activeDataset?.id ?? null,
    onMessage: (data) => {
      const msg = data as { answer?: string; error?: string; done?: boolean }
      setIsWaiting(false)
      if (msg.error) {
        setMessages((prev) => [...prev, {
          id: Date.now().toString(),
          role: 'assistant',
          content: msg.error!,
          isError: true,
        }])
      } else if (msg.answer) {
        setMessages((prev) => [...prev, {
          id: Date.now().toString(),
          role: 'assistant',
          content: msg.answer!,
        }])
      }
    },
  })

  // Clear messages when switching datasets
  useEffect(() => {
    setMessages([])
  }, [activeDataset?.id])

  // Fetch dataset-specific questions when dataset or tab changes
  // Depend on activeDataset.id + activeTab string so switching datasets always re-fires
  useEffect(() => {
    if (!activeDataset?.id || !activeTab) return
    setSuggestions([])
    setSuggestionsLoading(true)
    const id = activeDataset.id
    const tab = encodeURIComponent(activeTab)
    fetch(`/api/ai/${id}/suggested-questions/${tab}`)
      .then((r) => r.json())
      .then((data) => {
        const qs = data.questions
        setSuggestions(Array.isArray(qs) && qs.length >= 5 ? qs : FALLBACK_SUGGESTIONS)
      })
      .catch(() => setSuggestions(FALLBACK_SUGGESTIONS))
      .finally(() => setSuggestionsLoading(false))
  }, [activeDataset?.id, activeTab])

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages, isWaiting])

  const doSend = (text: string) => {
    const q = text.trim()
    if (!q || !connected || isWaiting) return
    setMessages((prev) => [...prev, { id: Date.now().toString(), role: 'user', content: q }])
    send({ question: q })
    setInput('')
    setIsWaiting(true)
    textareaRef.current?.focus()
  }

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) { e.preventDefault(); doSend(input) }
  }

  if (!activeDataset) {
    return (
      <div className="flex flex-col items-center justify-center h-full gap-3">
        <div className="w-16 h-16 rounded-2xl bg-blue-500/10 border border-blue-500/20 flex items-center justify-center text-3xl">💬</div>
        <p className="text-lg font-semibold text-gray-200">No dataset selected</p>
        <p className="text-sm text-gray-500">Go to Data Sources and select a dataset to start chatting</p>
      </div>
    )
  }

  const displayedSuggestions = suggestions.length ? suggestions : FALLBACK_SUGGESTIONS

  return (
    <div className="flex flex-col h-full max-h-full overflow-hidden">
      {/* Header */}
      <div className="flex items-center justify-between pb-3 border-b border-white/10 shrink-0">
        <div>
          <h2 className="text-xl font-bold text-white">AI Chat</h2>
          <p className="text-xs text-gray-400 mt-0.5">Powered by GPT-4o · {activeDataset.name}</p>
        </div>
        <div className={`flex items-center gap-2 text-xs px-3 py-1.5 rounded-full border font-medium ${
          connected
            ? 'bg-emerald-500/10 border-emerald-500/30 text-emerald-400'
            : 'bg-gray-800 border-gray-700 text-gray-500'
        }`}>
          <span className={`w-1.5 h-1.5 rounded-full ${connected ? 'bg-emerald-400 animate-pulse' : 'bg-gray-500'}`} />
          {connected ? 'Connected' : 'Connecting...'}
        </div>
      </div>

      {wsError && (
        <div className="mt-2 bg-red-500/10 border border-red-500/20 text-red-400 rounded-xl px-4 py-2 text-sm shrink-0">
          {wsError}
        </div>
      )}

      {/* Suggested questions — always visible, scrollable horizontally on small screens */}
      <div className="shrink-0 py-3 border-b border-white/8">
        <div className="flex items-center justify-between mb-2">
          <span className="text-xs text-gray-500 uppercase tracking-widest font-semibold">Suggested Questions</span>
          {suggestionsLoading && (
            <span className="flex items-center gap-1.5 text-xs text-gray-500">
              <span className="w-3 h-3 border border-blue-400 border-t-transparent rounded-full animate-spin" />
              Generating…
            </span>
          )}
        </div>

        {suggestionsLoading ? (
          <div className="grid grid-cols-2 lg:grid-cols-5 gap-1.5">
            {Array.from({ length: 10 }).map((_, i) => (
              <div key={i} className="h-10 rounded-lg animate-pulse" style={{ background: 'rgba(255,255,255,0.05)' }} />
            ))}
          </div>
        ) : (
          <div className="grid grid-cols-2 lg:grid-cols-5 gap-1.5">
            {displayedSuggestions.map((s, i) => (
              <button
                key={i}
                onClick={() => doSend(s)}
                disabled={!connected || isWaiting}
                title={s}
                className="text-left text-xs text-gray-300 rounded-lg px-2.5 py-2 transition-all disabled:opacity-40 flex items-start gap-1.5 leading-tight"
                style={{ background: 'rgba(255,255,255,0.04)', border: '1px solid rgba(255,255,255,0.08)' }}
                onMouseEnter={(e) => {
                  e.currentTarget.style.background = 'rgba(59,130,246,0.12)'
                  e.currentTarget.style.borderColor = 'rgba(59,130,246,0.4)'
                }}
                onMouseLeave={(e) => {
                  e.currentTarget.style.background = 'rgba(255,255,255,0.04)'
                  e.currentTarget.style.borderColor = 'rgba(255,255,255,0.08)'
                }}
              >
                <span className="shrink-0 text-xs">{CATEGORY_ICONS[i] ?? '💬'}</span>
                <span className="line-clamp-2">{s}</span>
              </button>
            ))}
          </div>
        )}
      </div>

      {/* Messages */}
      <div className="flex-1 overflow-y-auto py-4 space-y-4 pr-1">
        {messages.length === 0 && (
          <div className="flex flex-col items-center justify-center h-full gap-2 text-center pb-8">
            <span className="text-3xl">💬</span>
            <p className="text-gray-400 font-medium text-sm">Select a question above or type your own</p>
          </div>
        )}

        {messages.map((msg) => (
          <div key={msg.id} className={`flex gap-3 ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}>
            {msg.role === 'assistant' && (
              <div className="w-7 h-7 rounded-full bg-blue-600 flex items-center justify-center text-xs font-bold text-white shrink-0 mt-1">
                AI
              </div>
            )}
            <div className={`max-w-[80%] rounded-2xl px-4 py-3 text-sm leading-relaxed ${
              msg.role === 'user'
                ? 'bg-blue-600 text-white rounded-tr-sm'
                : msg.isError
                ? 'bg-red-500/10 text-red-400 border border-red-500/20 rounded-tl-sm'
                : 'bg-white/8 text-gray-100 border border-white/10 rounded-tl-sm'
            }`}>
              {msg.role === 'assistant' && !msg.isError ? (
                <ReactMarkdown
                  remarkPlugins={[remarkGfm]}
                  components={{
                    p: ({ children }) => <p className="mb-2 last:mb-0 leading-relaxed">{children}</p>,
                    strong: ({ children }) => <strong className="font-semibold text-white">{children}</strong>,
                    em: ({ children }) => <em className="text-blue-300 not-italic font-medium">{children}</em>,
                    ul: ({ children }) => <ul className="list-disc list-inside space-y-1 mb-3 text-gray-200">{children}</ul>,
                    ol: ({ children }) => <ol className="list-decimal list-inside space-y-1 mb-3 text-gray-200">{children}</ol>,
                    li: ({ children }) => <li className="text-gray-200 leading-relaxed">{children}</li>,
                    h1: ({ children }) => <h1 className="text-base font-bold text-white mb-2 mt-1">{children}</h1>,
                    h2: ({ children }) => <h2 className="text-sm font-bold text-blue-300 mb-2 mt-1 uppercase tracking-wide">{children}</h2>,
                    h3: ({ children }) => <h3 className="text-sm font-semibold text-gray-200 mb-1">{children}</h3>,
                    blockquote: ({ children }) => (
                      <blockquote className="border-l-2 border-blue-500 pl-3 my-2 text-gray-400 italic">{children}</blockquote>
                    ),
                    code: ({ children }) => (
                      <code className="bg-black/40 text-blue-300 rounded px-1.5 py-0.5 text-xs font-mono">{children}</code>
                    ),
                    pre: ({ children }) => (
                      <pre className="bg-black/50 border border-white/10 rounded-xl p-3 overflow-x-auto text-xs font-mono text-gray-200 mb-3">{children}</pre>
                    ),
                    table: ({ children }) => (
                      <div className="overflow-x-auto my-3 rounded-lg" style={{
                        border: '1px solid rgba(71,85,105,0.6)',
                        boxShadow: '0 4px 24px rgba(0,0,0,0.4)',
                      }}>
                        <table className="text-xs border-collapse w-full min-w-full">{children}</table>
                      </div>
                    ),
                    thead: ({ children }) => (
                      <thead style={{ background: 'linear-gradient(180deg, #1e293b 0%, #0f172a 100%)' }}>{children}</thead>
                    ),
                    tbody: ({ children }) => (
                      <tbody className="ai-table-body">{children}</tbody>
                    ),
                    tr: ({ children, ...props }) => (
                      <tr
                        className="ai-table-row border-b cursor-default"
                        style={{ borderColor: 'rgba(51,65,85,0.7)' }}
                        {...props}
                      >{children}</tr>
                    ),
                    th: ({ children }) => (
                      <th style={{ borderBottom: '2px solid rgba(59,130,246,0.5)', borderRight: '1px solid rgba(51,65,85,0.5)' }}
                        className="px-4 py-3 text-left text-xs font-semibold text-slate-300 uppercase tracking-widest whitespace-nowrap last:border-r-0">
                        {children}
                      </th>
                    ),
                    td: ({ children }) => (
                      <td style={{ borderRight: '1px solid rgba(51,65,85,0.4)' }}
                        className="px-4 py-2.5 text-slate-200 text-xs whitespace-nowrap last:border-r-0">
                        {children}
                      </td>
                    ),
                  }}
                >
                  {msg.content}
                </ReactMarkdown>
              ) : (
                msg.content
              )}
            </div>
            {msg.role === 'user' && (
              <div className="w-7 h-7 rounded-full bg-gray-600 flex items-center justify-center text-xs font-bold text-white shrink-0 mt-1">
                You
              </div>
            )}
          </div>
        ))}

        {isWaiting && (
          <div className="flex gap-3 justify-start">
            <div className="w-7 h-7 rounded-full bg-blue-600 flex items-center justify-center text-xs font-bold text-white shrink-0">
              AI
            </div>
            <div className="bg-white/8 border border-white/10 rounded-2xl rounded-tl-sm px-4 py-3">
              <div className="flex gap-1 items-center">
                {[0, 1, 2].map((i) => (
                  <span
                    key={i}
                    className="w-2 h-2 bg-blue-400 rounded-full animate-bounce"
                    style={{ animationDelay: `${i * 0.15}s` }}
                  />
                ))}
                <span className="text-xs text-gray-500 ml-2">Analyzing your data...</span>
              </div>
            </div>
          </div>
        )}
        <div ref={bottomRef} />
      </div>

      {/* Input bar */}
      <div className="shrink-0 pt-4 border-t border-white/10">
        <div className="flex gap-2 items-end bg-white/5 border border-white/10 rounded-2xl p-2 focus-within:border-blue-500/50 transition-colors">
          <textarea
            ref={textareaRef}
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={handleKeyDown}
            placeholder={connected ? 'Ask a question about your data… (Enter to send)' : 'Connecting to dataset...'}
            disabled={!connected || isWaiting}
            rows={2}
            className="flex-1 bg-transparent text-sm text-gray-100 placeholder-gray-500 resize-none focus:outline-none px-2 py-1 disabled:opacity-50"
          />
          <button
            onClick={() => doSend(input)}
            disabled={!input.trim() || !connected || isWaiting}
            className="px-4 py-2 bg-blue-600 hover:bg-blue-500 text-white text-sm font-medium rounded-xl transition-colors disabled:opacity-40 disabled:cursor-not-allowed shrink-0"
          >
            Send
          </button>
        </div>
        <p className="text-xs text-gray-600 mt-1.5 px-1">Shift+Enter for new line · Enter to send</p>
      </div>
    </div>
  )
}
