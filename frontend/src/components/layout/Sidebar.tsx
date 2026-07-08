import { NavLink } from 'react-router-dom'

const navGroups = [
  {
    label: 'Analytics',
    items: [
      { to: '/executive', label: 'Executive Dashboard', icon: '📊' },
      { to: '/analyst',   label: 'Analyst Workbench',  icon: '🔬' },
      { to: '/chat',      label: 'AI Chat',            icon: '💬' },
      { to: '/sources',   label: 'Data Sources',       icon: '📁' },
    ],
  },
  {
    label: 'About',
    items: [
      { to: '/usecases', label: 'Use Cases',    icon: '🏢' },
      { to: '/roi',      label: 'ROI & Benefits', icon: '📈' },
    ],
  },
]

export function Sidebar() {
  return (
    <aside className="w-60 flex flex-col h-full shrink-0"
      style={{ background: 'rgba(255,255,255,0.03)', borderRight: '1px solid rgba(255,255,255,0.07)' }}>
      {/* Logo */}
      <div className="px-5 py-5 border-b" style={{ borderColor: 'rgba(255,255,255,0.07)' }}>
        <div className="flex items-center gap-2.5">
          <div className="w-8 h-8 rounded-lg bg-blue-600 flex items-center justify-center text-sm font-bold text-white shadow-lg shadow-blue-500/30">
            P
          </div>
          <div>
            <h1 className="text-sm font-bold text-white leading-none">PulseAI</h1>
            <p className="text-xs text-gray-500 mt-0.5">Data Analytics</p>
          </div>
        </div>
      </div>

      {/* Nav */}
      <nav className="flex-1 p-3 space-y-4 overflow-y-auto">
        {navGroups.map((group) => (
          <div key={group.label}>
            <p className="text-xs text-gray-600 uppercase tracking-widest font-medium px-3 py-1.5">{group.label}</p>
            <div className="space-y-0.5">
              {group.items.map(({ to, label, icon }) => (
                <NavLink
                  key={to}
                  to={to}
                  className={({ isActive }) =>
                    `flex items-center gap-3 px-3 py-2.5 rounded-xl text-sm transition-all font-medium ${
                      isActive
                        ? 'bg-blue-600/20 text-blue-400 border border-blue-500/20'
                        : 'text-gray-400 hover:text-gray-200 hover:bg-white/5'
                    }`
                  }
                >
                  <span className="text-base">{icon}</span>
                  <span>{label}</span>
                </NavLink>
              ))}
            </div>
          </div>
        ))}
      </nav>

      {/* Footer */}
      <div className="px-5 py-4 border-t" style={{ borderColor: 'rgba(255,255,255,0.07)' }}>
        <p className="text-xs text-gray-600">Powered by GPT-4o</p>
        <p className="text-xs text-gray-700 mt-0.5">Accenture GenAI Gateway</p>
      </div>
    </aside>
  )
}
