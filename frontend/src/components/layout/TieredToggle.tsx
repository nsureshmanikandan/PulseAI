import { useAppStore } from '../../store/useAppStore'

export function TieredToggle() {
  const tier = useAppStore((s) => s.tier)
  const setTier = useAppStore((s) => s.setTier)

  return (
    <div className="flex items-center gap-1 rounded-xl p-1" style={{ background: 'rgba(255,255,255,0.06)', border: '1px solid rgba(255,255,255,0.08)' }}>
      {(['executive', 'analyst'] as const).map((t) => (
        <button
          key={t}
          onClick={() => setTier(t)}
          className={`px-4 py-1.5 rounded-lg text-xs font-semibold transition-all capitalize ${
            tier === t
              ? 'bg-blue-600 text-white shadow-sm shadow-blue-500/30'
              : 'text-gray-400 hover:text-gray-200'
          }`}
        >
          {t}
        </button>
      ))}
    </div>
  )
}
