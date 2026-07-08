import { useAppStore } from '../../store/useAppStore'
import { TieredToggle } from './TieredToggle'

export function TopBar() {
  const activeDataset = useAppStore((s) => s.activeDataset)
  const activeTab     = useAppStore((s) => s.activeTab)
  const setActiveTab  = useAppStore((s) => s.setActiveTab)

  const tabs = activeDataset?.tabNames ?? []

  return (
    <header className="h-14 shrink-0 border-b flex items-center justify-between px-6 gap-4"
      style={{ background: 'rgba(255,255,255,0.03)', borderColor: 'rgba(255,255,255,0.08)' }}>

      {/* Left: dataset name + tab picker */}
      <div className="flex items-center gap-3 min-w-0">
        {activeDataset ? (
          <>
            <span className="text-sm text-gray-400 shrink-0">
              Dataset: <span className="font-semibold text-white">{activeDataset.name}</span>
            </span>

            {tabs.length > 1 && (
              <>
                <span className="text-gray-600 text-xs shrink-0">|</span>
                <div className="flex items-center gap-1 overflow-x-auto no-scrollbar">
                  {tabs.map((tab) => (
                    <button
                      key={tab}
                      onClick={() => setActiveTab(tab)}
                      className={`shrink-0 text-xs px-3 py-1 rounded-full border transition-all font-medium ${
                        activeTab === tab
                          ? 'bg-blue-600 border-blue-500 text-white'
                          : 'border-white/10 text-gray-400 hover:border-blue-500/40 hover:text-gray-200'
                      }`}
                      style={activeTab !== tab ? { background: 'rgba(255,255,255,0.04)' } : {}}
                    >
                      {tab}
                    </button>
                  ))}
                </div>
              </>
            )}

            {tabs.length === 1 && activeTab && (
              <span className="text-xs text-gray-500 border border-white/10 rounded-full px-2.5 py-0.5"
                style={{ background: 'rgba(255,255,255,0.04)' }}>
                {activeTab}
              </span>
            )}
          </>
        ) : (
          <span className="text-sm text-gray-600">No dataset selected</span>
        )}
      </div>

      <TieredToggle />
    </header>
  )
}
