import { NavLink } from 'react-router-dom'

const navItems = [
  { to: '/executive', label: 'Executive Dashboard', icon: '📊' },
  { to: '/analyst', label: 'Analyst Workbench', icon: '🔬' },
  { to: '/chat', label: 'AI Chat', icon: '💬' },
  { to: '/sources', label: 'Data Sources', icon: '📁' },
]

export function Sidebar() {
  return (
    <aside className="w-64 bg-gray-900 text-white flex flex-col h-full">
      <div className="p-6 border-b border-gray-700">
        <h1 className="text-xl font-bold text-blue-400">PulseAI</h1>
        <p className="text-xs text-gray-400 mt-1">Real-time pulse of your data</p>
      </div>
      <nav className="flex-1 p-4 space-y-1">
        {navItems.map(({ to, label, icon }) => (
          <NavLink
            key={to}
            to={to}
            className={({ isActive }) =>
              `flex items-center gap-3 px-3 py-2 rounded-lg text-sm transition-colors ${
                isActive
                  ? 'bg-blue-600 text-white'
                  : 'text-gray-300 hover:bg-gray-700'
              }`
            }
          >
            <span>{icon}</span>
            <span>{label}</span>
          </NavLink>
        ))}
      </nav>
    </aside>
  )
}
