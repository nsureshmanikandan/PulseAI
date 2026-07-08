export function ROIBenefits() {
  const bigStats = [
    { val: '95%', unit: 'Faster', desc: 'Time to insight vs manual Excel analysis', color: '#3b82f6', icon: '⚡' },
    { val: 'Zero', unit: 'Code', desc: 'No SQL, Python, or BI tool training needed', color: '#10b981', icon: '🚫' },
    { val: '< 2', unit: 'Minutes', desc: 'From file upload to first actionable insight', color: '#f59e0b', icon: '⏱️' },
    { val: '10x', unit: 'More', desc: 'Questions answered per analyst per day', color: '#8b5cf6', icon: '📈' },
  ]

  const personas = [
    {
      color: '#3b82f6', colorDim: 'rgba(59,130,246,0.1)', colorBorder: 'rgba(59,130,246,0.25)',
      icon: '👔', title: 'Business Leaders',
      benefits: [
        { icon: '📊', b: 'Board-ready dashboards in minutes, not days' },
        { icon: '🤖', b: 'AI-written narrative — no analyst briefing needed' },
        { icon: '✅', b: 'Confident decisions backed by actual data' },
        { icon: '🗂️', b: 'All Excel tabs in one unified, visual view' },
        { icon: '🔔', b: 'Auto-detected anomalies and risk alerts' },
      ],
    },
    {
      color: '#6366f1', colorDim: 'rgba(99,102,241,0.1)', colorBorder: 'rgba(99,102,241,0.25)',
      icon: '🔬', title: 'Data Analysts',
      benefits: [
        { icon: '⚡', b: 'Skip manual chart building — 6 types auto-generated' },
        { icon: '🖱️', b: 'Self-service workbench — no IT ticket needed' },
        { icon: '📐', b: 'Custom charts with 2-click column selection' },
        { icon: '🔗', b: 'Cross-tab relationships surfaced automatically' },
        { icon: '📤', b: 'Export-ready Plotly visualizations' },
      ],
    },
    {
      color: '#10b981', colorDim: 'rgba(16,185,129,0.1)', colorBorder: 'rgba(16,185,129,0.25)',
      icon: '🛠️', title: 'IT & Data Teams',
      benefits: [
        { icon: '🏗️', b: 'Zero infrastructure change — works with SQLite locally' },
        { icon: '📂', b: 'Works with existing Excel & CSV files immediately' },
        { icon: '🔒', b: 'Data stays local — nothing leaves your environment' },
        { icon: '🔄', b: 'Pluggable LLM — swap GPT-4o for any provider' },
        { icon: '🧩', b: 'FastAPI + React stack — easy to extend' },
      ],
    },
    {
      color: '#f59e0b', colorDim: 'rgba(245,158,11,0.1)', colorBorder: 'rgba(245,158,11,0.25)',
      icon: '💰', title: 'Finance & Risk',
      benefits: [
        { icon: '⚠️', b: 'Instant loan portfolio risk view on upload' },
        { icon: '🎯', b: 'Default & outlier auto-detection, no config' },
        { icon: '📋', b: 'Cross-tab drill-down without SQL knowledge' },
        { icon: '📑', b: 'Audit-ready filtered tables from AI chat' },
        { icon: '📉', b: 'DPD, LTV, credit score KPIs in one view' },
      ],
    },
  ]

  const comparisons = [
    { task: 'Get KPI summary from Excel', before: '2–4 hours (manual pivot tables)', after: '< 30 seconds', saving: '99%' },
    { task: 'Build 6 charts for a report', before: '1–2 days (BI tool setup)', after: '< 1 minute (auto-generated)', saving: '99%' },
    { task: 'Answer "show me top 10 loans"', before: 'SQL query + DBA involvement', after: 'Type in AI Chat', saving: '100%' },
    { task: 'Explain data to leadership', before: 'Analyst write-up (3–5 hours)', after: 'AI narrative (instant)', saving: '98%' },
    { task: 'Detect outliers/anomalies', before: 'Data science model (days)', after: 'Auto-detected on upload', saving: '100%' },
    { task: 'Cross-tab analysis (2 columns)', before: 'Python/pandas (30 min setup)', after: 'Ask AI in plain English', saving: '99%' },
  ]

  const techBenefits = [
    { icon: '🌐', title: 'Browser-Based', body: '100% web UI — no desktop app, no install, works on any device.' },
    { icon: '🔌', title: 'No Integration', body: 'Upload a file and start — no database connectors or ETL pipelines.' },
    { icon: '🤝', title: 'Multi-Tab Excel', body: 'All 6 tabs loaded with FK relationships auto-detected.' },
    { icon: '🧠', title: 'GPT-4o Powered', body: 'Frontier AI for accurate narratives, tables, and insights.' },
    { icon: '🎨', title: 'Enterprise Dark UI', body: 'Professional dark theme with animated charts and shimmer loading.' },
    { icon: '📡', title: 'Real-Time Chat', body: 'WebSocket AI chat — responses stream instantly, no page refresh.' },
  ]

  return (
    <div className="space-y-8 pb-8">
      {/* Header */}
      <div>
        <div className="flex items-center gap-3 mb-1">
          <span className="text-xs font-bold text-emerald-400 uppercase tracking-widest px-3 py-1 rounded-full border border-emerald-500/30"
            style={{ background: 'rgba(16,185,129,0.1)' }}>
            ROI & BENEFITS
          </span>
        </div>
        <h1 className="text-2xl font-bold text-white mt-2">Return on Investment</h1>
        <p className="text-gray-400 mt-1 text-sm">
          Quantified value delivered to every stakeholder — from business leaders to data engineers.
        </p>
      </div>

      {/* Big stats */}
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
        {bigStats.map((s) => (
          <div key={s.val} className="rounded-2xl p-5 border relative overflow-hidden"
            style={{ background: 'rgba(15,23,42,0.8)', borderColor: `${s.color}33` }}>
            <div className="absolute top-0 left-0 right-0 h-0.5" style={{ background: s.color }} />
            <div className="text-3xl mb-2">{s.icon}</div>
            <div className="text-4xl font-black mb-0.5" style={{ color: s.color }}>{s.val}</div>
            <div className="text-sm font-semibold text-white mb-1">{s.unit}</div>
            <div className="text-xs text-gray-500 leading-snug">{s.desc}</div>
          </div>
        ))}
      </div>

      {/* Before vs After comparison table */}
      <div className="rounded-2xl border overflow-hidden"
        style={{ background: 'rgba(15,23,42,0.6)', borderColor: 'rgba(255,255,255,0.08)' }}>
        <div className="px-5 py-4 border-b" style={{ borderColor: 'rgba(255,255,255,0.07)', background: 'rgba(0,0,0,0.2)' }}>
          <p className="text-sm font-bold text-white">Before PulseAI vs After PulseAI</p>
          <p className="text-xs text-gray-500 mt-0.5">Time savings per common analytics task</p>
        </div>
        <div className="overflow-x-auto">
          <table className="w-full text-xs">
            <thead style={{ background: 'linear-gradient(90deg, rgba(59,130,246,0.15), rgba(99,102,241,0.15))' }}>
              <tr>
                <th className="px-4 py-3 text-left font-semibold text-slate-300 uppercase tracking-wider border-b border-white/10">Task</th>
                <th className="px-4 py-3 text-left font-semibold text-red-400 uppercase tracking-wider border-b border-white/10">Before</th>
                <th className="px-4 py-3 text-left font-semibold text-emerald-400 uppercase tracking-wider border-b border-white/10">With PulseAI</th>
                <th className="px-4 py-3 text-center font-semibold text-blue-400 uppercase tracking-wider border-b border-white/10">Time Saved</th>
              </tr>
            </thead>
            <tbody>
              {comparisons.map((row, i) => (
                <tr key={i} className="border-b transition-all duration-100"
                  style={{
                    borderColor: 'rgba(51,65,85,0.5)',
                    background: i % 2 === 0 ? 'rgba(15,23,42,0.6)' : 'rgba(30,41,59,0.5)',
                  }}
                  onMouseEnter={e => (e.currentTarget.style.background = 'rgba(59,130,246,0.1)')}
                  onMouseLeave={e => (e.currentTarget.style.background = i % 2 === 0 ? 'rgba(15,23,42,0.6)' : 'rgba(30,41,59,0.5)')}>
                  <td className="px-4 py-3 text-gray-200 font-medium">{row.task}</td>
                  <td className="px-4 py-3 text-red-400">{row.before}</td>
                  <td className="px-4 py-3 text-emerald-400 font-medium">{row.after}</td>
                  <td className="px-4 py-3 text-center">
                    <span className="px-2.5 py-1 rounded-full text-xs font-bold text-black"
                      style={{ background: '#10b981' }}>{row.saving}</span>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

      {/* Persona benefit cards */}
      <div>
        <p className="text-xs text-gray-500 uppercase tracking-widest font-semibold mb-4">Benefits by Role</p>
        <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-4 gap-4">
          {personas.map((p) => (
            <div key={p.title} className="rounded-2xl border overflow-hidden"
              style={{ background: 'rgba(15,23,42,0.6)', borderColor: p.colorBorder }}>
              <div className="h-0.5" style={{ background: p.color }} />
              <div className="p-4">
                <div className="flex items-center gap-2.5 mb-4">
                  <div className="w-9 h-9 rounded-xl flex items-center justify-center text-xl"
                    style={{ background: p.colorDim, border: `1px solid ${p.colorBorder}` }}>
                    {p.icon}
                  </div>
                  <span className="text-sm font-bold text-white">{p.title}</span>
                </div>
                <div className="space-y-2.5">
                  {p.benefits.map((b, i) => (
                    <div key={i} className="flex items-start gap-2">
                      <span className="shrink-0 text-sm">{b.icon}</span>
                      <span className="text-xs text-gray-300 leading-snug">{b.b}</span>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Technical benefits */}
      <div>
        <p className="text-xs text-gray-500 uppercase tracking-widest font-semibold mb-4">Technical Advantages</p>
        <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-3">
          {techBenefits.map((t) => (
            <div key={t.title} className="rounded-xl p-4 border text-center"
              style={{ background: 'rgba(15,23,42,0.6)', borderColor: 'rgba(255,255,255,0.07)' }}>
              <div className="text-2xl mb-2">{t.icon}</div>
              <div className="text-xs font-bold text-white mb-1">{t.title}</div>
              <div className="text-xs text-gray-500 leading-snug">{t.body}</div>
            </div>
          ))}
        </div>
      </div>

      {/* Summary banner */}
      <div className="rounded-2xl p-6 border"
        style={{ background: 'linear-gradient(135deg, rgba(59,130,246,0.1), rgba(99,102,241,0.1))', borderColor: 'rgba(99,102,241,0.3)' }}>
        <div className="flex flex-col md:flex-row items-center justify-between gap-4">
          <div>
            <p className="text-lg font-bold text-white">PulseAI delivers enterprise analytics to everyone</p>
            <p className="text-sm text-gray-400 mt-1">
              No data science degree. No BI license. No SQL. Just upload, ask, and decide.
            </p>
          </div>
          <div className="flex gap-3 shrink-0">
            <a href="/sources"
              className="px-5 py-2.5 bg-blue-600 hover:bg-blue-500 text-white text-sm font-semibold rounded-xl transition-colors whitespace-nowrap">
              Try Now →
            </a>
            <a href="/usecases"
              className="px-5 py-2.5 text-gray-300 text-sm font-semibold rounded-xl transition-colors whitespace-nowrap border border-white/10 hover:border-white/20"
              style={{ background: 'rgba(255,255,255,0.05)' }}>
              See Use Cases
            </a>
          </div>
        </div>
      </div>
    </div>
  )
}

export default ROIBenefits
