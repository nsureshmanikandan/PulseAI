import { useAppStore } from '../../store/useAppStore'
import { TieredToggle } from './TieredToggle'

export function TopBar() {
  const activeDataset = useAppStore((s) => s.activeDataset)

  return (
    <header className="h-14 bg-white border-b border-gray-200 flex items-center justify-between px-6 shrink-0">
      <div className="text-sm text-gray-600">
        {activeDataset ? (
          <span>
            Dataset: <span className="font-medium text-gray-900">{activeDataset.name}</span>
          </span>
        ) : (
          <span className="text-gray-400">No dataset selected</span>
        )}
      </div>
      <TieredToggle />
    </header>
  )
}
