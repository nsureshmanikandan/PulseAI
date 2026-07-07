import { useState, useRef, useEffect } from 'react'
import { useAppStore } from '../../store/useAppStore'
import { useWebSocket } from '../../hooks/useWebSocket'

interface Message {
  id: string
  role: 'user' | 'assistant'
  content: string
  isError?: boolean
}

export function AIChat() {
  const activeDataset = useAppStore((s) => s.activeDataset)
  const [messages, setMessages] = useState<Message[]>([])
  const [input, setInput] = useState('')
  const [isWaiting, setIsWaiting] = useState(false)
  const bottomRef = useRef<HTMLDivElement>(null)

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

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages])

  const handleSend = () => {
    if (!input.trim() || !connected) return
    const userMsg: Message = { id: Date.now().toString(), role: 'user', content: input }
    setMessages((prev) => [...prev, userMsg])
    send({ question: input })
    setInput('')
    setIsWaiting(true)
  }

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      handleSend()
    }
  }

  if (!activeDataset) {
    return (
      <div className="flex flex-col items-center justify-center h-full text-gray-400">
        <span className="text-5xl mb-4">💬</span>
        <p className="text-lg font-medium">No dataset selected</p>
        <p className="text-sm mt-1">Upload a file or select a dataset to start chatting</p>
      </div>
    )
  }

  return (
    <div className="flex flex-col h-full">
      {/* Header */}
      <div className="flex items-center justify-between mb-4 shrink-0">
        <div>
          <h2 className="text-2xl font-bold text-gray-900">AI Chat</h2>
          <p className="text-sm text-gray-500 mt-1">{activeDataset.name}</p>
        </div>
        <div className={`flex items-center gap-2 text-xs px-3 py-1 rounded-full ${
          connected ? 'bg-green-50 text-green-700' : 'bg-gray-100 text-gray-500'
        }`}>
          <span className={`w-1.5 h-1.5 rounded-full ${connected ? 'bg-green-500' : 'bg-gray-400'}`} />
          {connected ? 'Connected' : 'Disconnected'}
        </div>
      </div>

      {wsError && (
        <div className="mb-4 bg-red-50 border border-red-200 text-red-700 rounded-lg px-4 py-2 text-sm shrink-0">
          {wsError}
        </div>
      )}

      {/* Messages */}
      <div className="flex-1 overflow-y-auto space-y-4 pb-4">
        {messages.length === 0 && (
          <div className="text-center text-gray-400 mt-12">
            <p className="text-lg">Ask anything about your data</p>
            <p className="text-sm mt-2">Try: "What is the total revenue?" or "Show top 5 categories"</p>
          </div>
        )}
        {messages.map((msg) => (
          <div key={msg.id} className={`flex ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}>
            <div className={`max-w-[75%] rounded-2xl px-4 py-3 text-sm ${
              msg.role === 'user'
                ? 'bg-blue-600 text-white'
                : msg.isError
                ? 'bg-red-50 text-red-700 border border-red-200'
                : 'bg-white text-gray-800 border border-gray-200'
            }`}>
              {msg.content}
            </div>
          </div>
        ))}
        {isWaiting && (
          <div className="flex justify-start">
            <div className="bg-white border border-gray-200 rounded-2xl px-4 py-3">
              <div className="flex gap-1">
                {[0, 1, 2].map((i) => (
                  <span key={i} className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: `${i * 0.15}s` }} />
                ))}
              </div>
            </div>
          </div>
        )}
        <div ref={bottomRef} />
      </div>

      {/* Input */}
      <div className="flex gap-3 shrink-0 pt-4 border-t border-gray-200">
        <textarea
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={handleKeyDown}
          placeholder={connected ? 'Ask a question about your data...' : 'Connecting...'}
          disabled={!connected || isWaiting}
          rows={2}
          className="flex-1 text-sm border border-gray-300 rounded-xl px-4 py-3 resize-none focus:outline-none focus:ring-2 focus:ring-blue-500 disabled:bg-gray-50 disabled:text-gray-400"
        />
        <button
          onClick={handleSend}
          disabled={!input.trim() || !connected || isWaiting}
          className="px-4 py-2 bg-blue-600 text-white rounded-xl hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors self-end"
        >
          Send
        </button>
      </div>
    </div>
  )
}
