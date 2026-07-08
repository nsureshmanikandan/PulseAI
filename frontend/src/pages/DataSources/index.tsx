import { useRef, useEffect, useState } from 'react'
import { useDataset } from '../../hooks/useDataset'
import { useAppStore } from '../../store/useAppStore'

interface Relationship {
  tab_a: string
  column_a: string
  tab_b: string
  column_b: string
  confidence: string | null
}

export function DataSources() {
  const { datasets, loading, uploading, error, uploadDataset, deleteDataset, selectDataset } = useDataset()
  const activeDataset = useAppStore((s) => s.activeDataset)
  const fileInputRef = useRef<HTMLInputElement>(null)
  const [relationships, setRelationships] = useState<Relationship[]>([])
  const [relsLoading, setRelsLoading] = useState(false)

  useEffect(() => {
    if (!activeDataset?.id) { setRelationships([]); return }
    setRelsLoading(true)
    fetch(`/api/datasets/${activeDataset.id}/relationships`)
      .then(r => r.json())
      .then(data => setRelationships(Array.isArray(data) ? data : []))
      .catch(() => setRelationships([]))
      .finally(() => setRelsLoading(false))
  }, [activeDataset?.id])

  const handleFileChange = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0]
    if (!file) return
    await uploadDataset(file)
    if (fileInputRef.current) fileInputRef.current.value = ''
  }

  const tabCount = (ds: { tab_names?: string | string[] | null }) => {
    if (!ds.tab_names) return 1
    if (Array.isArray(ds.tab_names)) return ds.tab_names.length
    try { return JSON.parse(ds.tab_names as string).length } catch { return 1 }
  }

  const tabList = (ds: { tab_names?: string | string[] | null }): string[] => {
    if (!ds.tab_names) return []
    if (Array.isArray(ds.tab_names)) return ds.tab_names
    try { return JSON.parse(ds.tab_names as string) } catch { return [] }
  }

  return (
    <div className="space-y-6 pb-8">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <div className="flex items-center gap-3 mb-1">
            <span className="text-xs font-bold text-blue-400 uppercase tracking-widest px-3 py-1 rounded-full border border-blue-500/30"
              style={{ background: 'rgba(59,130,246,0.1)' }}>
              DATA SOURCES
            </span>
          </div>
          <h1 className="text-2xl font-bold text-white mt-1">Manage Datasets</h1>
          <p className="text-gray-400 mt-0.5 text-sm">Upload Excel or CSV files — multi-tab supported, FK relationships auto-detected.</p>
        </div>
        <div>
          <input ref={fileInputRef} type="file" accept=".xlsx,.xls,.csv" onChange={handleFileChange} className="hidden" id="file-upload" />
          <label htmlFor="file-upload"
            className={`cursor-pointer inline-flex items-center gap-2 px-5 py-2.5 bg-blue-600 hover:bg-blue-500 text-white text-sm font-semibold rounded-xl transition-colors ${uploading ? 'opacity-50 pointer-events-none' : ''}`}>
            {uploading ? (
              <><span className="w-4 h-4 border-2 border-white/30 border-t-white rounded-full animate-spin" />Uploading…</>
            ) : (
              <><span className="text-base">+</span> Upload File</>
            )}
          </label>
        </div>
      </div>

      {error && (
        <div className="rounded-xl border border-red-500/30 px-4 py-3 text-sm text-red-400"
          style={{ background: 'rgba(239,68,68,0.08)' }}>{error}</div>
      )}

      {/* Dataset list */}
      {loading ? (
        <div className="space-y-3">
          {[1, 2, 3].map(i => (
            <div key={i} className="rounded-2xl border p-4 animate-pulse"
              style={{ background: 'rgba(15,23,42,0.6)', borderColor: 'rgba(255,255,255,0.07)' }}>
              <div className="h-4 rounded w-1/3 mb-2" style={{ background: 'rgba(255,255,255,0.08)' }} />
              <div className="h-3 rounded w-1/4" style={{ background: 'rgba(255,255,255,0.05)' }} />
            </div>
          ))}
        </div>
      ) : datasets.length === 0 ? (
        <div className="flex flex-col items-center justify-center rounded-2xl border-2 border-dashed py-16 text-gray-500"
          style={{ borderColor: 'rgba(255,255,255,0.1)' }}>
          <span className="text-5xl mb-4">📂</span>
          <p className="font-semibold text-gray-400">No datasets yet</p>
          <p className="text-sm mt-1">Upload an Excel or CSV file to get started</p>
        </div>
      ) : (
        <div className="space-y-3">
          {datasets.map((ds) => {
            const isActive = activeDataset?.id === ds.id
            const tabs = tabList(ds)
            const count = tabCount(ds)
            return (
              <div key={ds.id} className="rounded-2xl border overflow-hidden transition-all"
                style={{
                  background: 'rgba(15,23,42,0.6)',
                  borderColor: isActive ? 'rgba(59,130,246,0.5)' : 'rgba(255,255,255,0.07)',
                  boxShadow: isActive ? '0 0 0 1px rgba(59,130,246,0.2)' : 'none',
                }}>
                {isActive && <div className="h-0.5" style={{ background: '#3b82f6' }} />}
                <div className="p-4 flex items-center justify-between gap-3">
                  <div className="flex items-center gap-3 flex-1 min-w-0">
                    <div className="w-10 h-10 rounded-xl flex items-center justify-center text-xl shrink-0"
                      style={{ background: isActive ? 'rgba(59,130,246,0.15)' : 'rgba(255,255,255,0.05)', border: `1px solid ${isActive ? 'rgba(59,130,246,0.3)' : 'rgba(255,255,255,0.08)'}` }}>
                      📊
                    </div>
                    <div className="min-w-0">
                      <p className="font-semibold text-white truncate">{ds.name}</p>
                      <div className="flex items-center gap-2 mt-1 flex-wrap">
                        <span className="text-xs px-2 py-0.5 rounded-full font-medium"
                          style={{ background: 'rgba(59,130,246,0.15)', color: '#60a5fa', border: '1px solid rgba(59,130,246,0.25)' }}>
                          {count} tab{count !== 1 ? 's' : ''}
                        </span>
                        {tabs.slice(0, 5).map(t => (
                          <span key={t} className="text-xs text-gray-500 px-2 py-0.5 rounded border"
                            style={{ background: 'rgba(255,255,255,0.03)', borderColor: 'rgba(255,255,255,0.08)' }}>
                            {t}
                          </span>
                        ))}
                        {tabs.length > 5 && <span className="text-xs text-gray-600">+{tabs.length - 5} more</span>}
                      </div>
                    </div>
                  </div>
                  <div className="flex items-center gap-2 ml-4 shrink-0">
                    <button onClick={() => selectDataset(ds)}
                      className="px-4 py-1.5 text-sm font-semibold rounded-lg transition-colors"
                      style={isActive
                        ? { background: 'rgba(59,130,246,0.2)', color: '#60a5fa', border: '1px solid rgba(59,130,246,0.3)' }
                        : { background: 'rgba(59,130,246,0.1)', color: '#93c5fd', border: '1px solid rgba(59,130,246,0.2)' }}>
                      {isActive ? '✓ Active' : 'Select'}
                    </button>
                    <button onClick={() => deleteDataset(ds.id)}
                      className="px-4 py-1.5 text-sm font-semibold rounded-lg transition-colors"
                      style={{ background: 'rgba(239,68,68,0.1)', color: '#f87171', border: '1px solid rgba(239,68,68,0.2)' }}>
                      Delete
                    </button>
                  </div>
                </div>
              </div>
            )
          })}
        </div>
      )}

      {/* FK Relationships panel — shown when active dataset has relationships */}
      {activeDataset && (
        <div className="rounded-2xl border overflow-hidden" style={{ background: 'rgba(15,23,42,0.6)', borderColor: 'rgba(255,255,255,0.08)' }}>
          <div className="px-5 py-4 border-b flex items-center gap-3"
            style={{ borderColor: 'rgba(255,255,255,0.07)', background: 'rgba(0,0,0,0.2)' }}>
            <span className="text-lg">🔗</span>
            <div>
              <p className="text-sm font-bold text-white">FK Relationships Detected</p>
              <p className="text-xs text-gray-500 mt-0.5">Auto-detected cross-tab foreign key links in <span className="text-blue-400">{activeDataset.name}</span></p>
            </div>
            {!relsLoading && (
              <span className="ml-auto text-xs font-bold px-2.5 py-1 rounded-full"
                style={{ background: relationships.length > 0 ? 'rgba(16,185,129,0.15)' : 'rgba(100,116,139,0.15)', color: relationships.length > 0 ? '#34d399' : '#64748b', border: `1px solid ${relationships.length > 0 ? 'rgba(16,185,129,0.3)' : 'rgba(100,116,139,0.2)'}` }}>
                {relationships.length} link{relationships.length !== 1 ? 's' : ''} found
              </span>
            )}
          </div>

          <div className="p-5">
            {relsLoading ? (
              <div className="space-y-2">
                {[1, 2, 3].map(i => (
                  <div key={i} className="h-10 rounded-xl animate-pulse" style={{ background: 'rgba(255,255,255,0.05)' }} />
                ))}
              </div>
            ) : relationships.length === 0 ? (
              <div className="text-center py-8 text-gray-500">
                <span className="text-3xl block mb-2">🔍</span>
                <p className="text-sm">No FK relationships detected.</p>
                <p className="text-xs mt-1">Upload a multi-tab Excel file (e.g. with customer_id linking multiple sheets) to see cross-tab relationships here.</p>
              </div>
            ) : (
              <div className="space-y-2">
                {relationships.map((rel, i) => (
                  <div key={i} className="flex items-center gap-3 rounded-xl px-4 py-3 border"
                    style={{ background: 'rgba(99,102,241,0.06)', borderColor: 'rgba(99,102,241,0.2)' }}>
                    {/* Tab A */}
                    <div className="flex flex-col min-w-0">
                      <span className="text-xs font-bold text-blue-400">{rel.tab_a}</span>
                      <span className="text-xs text-gray-400 font-mono">{rel.column_a}</span>
                    </div>

                    {/* Arrow */}
                    <div className="flex items-center gap-1 shrink-0">
                      <div className="w-8 h-px" style={{ background: '#6366f1' }} />
                      <span className="text-indigo-400 text-xs font-bold">→</span>
                      <div className="w-8 h-px" style={{ background: '#6366f1' }} />
                    </div>

                    {/* Tab B */}
                    <div className="flex flex-col min-w-0 flex-1">
                      <span className="text-xs font-bold text-indigo-400">{rel.tab_b}</span>
                      <span className="text-xs text-gray-400 font-mono">{rel.column_b}</span>
                    </div>

                    {/* Confidence */}
                    {rel.confidence && (
                      <span className="text-xs px-2 py-0.5 rounded-full shrink-0"
                        style={{ background: 'rgba(16,185,129,0.12)', color: '#34d399', border: '1px solid rgba(16,185,129,0.25)' }}>
                        {rel.confidence}
                      </span>
                    )}
                  </div>
                ))}

                <p className="text-xs text-gray-600 mt-3 px-1">
                  These links are used automatically when you ask cross-tab questions in AI Chat — e.g. "join Customers and Loans by customer_id".
                </p>
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  )
}
