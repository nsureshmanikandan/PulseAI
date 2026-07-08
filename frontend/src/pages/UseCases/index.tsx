export function UseCases() {
  const cases = [
    {
      color: '#3b82f6',
      colorDim: 'rgba(59,130,246,0.12)',
      colorBorder: 'rgba(59,130,246,0.3)',
      icon: '🏦',
      domain: 'Banking & Financial Services',
      title: 'Loan Portfolio Risk Management',
      description:
        'Upload your loan portfolio Excel. Instantly surface default-risk customers, outstanding balance concentration, collateral coverage gaps, and days-past-due trends — without writing a single SQL query.',
      questions: [
        'Show all loans where dpd > 60 as a table',
        'Top 10 customers by outstanding balance',
        'Cross-tab: loan_type vs loan_status',
        'What % of loans are in Default or Watch status?',
        'Correlation between credit_score and outstanding_balance',
      ],
      metrics: [
        { val: '28%', label: 'Default + Watch Rate', c: '#ef4444' },
        { val: '$743.9M', label: 'Total Outstanding', c: '#3b82f6' },
        { val: '657', label: 'Avg Credit Score', c: '#10b981' },
      ],
      tag: 'RISK',
      tagColor: '#ef4444',
    },
    {
      color: '#10b981',
      colorDim: 'rgba(16,185,129,0.12)',
      colorBorder: 'rgba(16,185,129,0.3)',
      icon: '🛡️',
      domain: 'Insurance',
      title: 'Claims Analytics & Fraud Detection',
      description:
        'Analyze claims history CSV files. Spot high-frequency claimants, detect statistical outliers that indicate fraud, and identify seasonal patterns — all through natural language questions to the AI.',
      questions: [
        'Show claims where amount > 50000 as a table',
        'Which claimants appear more than 3 times?',
        'Distribution of claim amounts by region',
        'Are there outliers in claim processing time?',
        'Group by claim_type and show average payout',
      ],
      metrics: [
        { val: '40%', label: 'Fraud-Flagged Claims', c: '#f59e0b' },
        { val: '180', label: 'Fraud Indicators Found', c: '#ef4444' },
        { val: '61 days', label: 'Avg Processing Time', c: '#10b981' },
      ],
      tag: 'FRAUD',
      tagColor: '#f59e0b',
    },
    {
      color: '#8b5cf6',
      colorDim: 'rgba(139,92,246,0.12)',
      colorBorder: 'rgba(139,92,246,0.3)',
      icon: '🛒',
      domain: 'Retail & E-Commerce',
      title: 'Sales Performance & Product Intelligence',
      description:
        'Drop in monthly sales Excel. Get instant revenue KPIs, top and bottom product performers, regional breakdowns, and an AI-written executive summary ready to paste into a board report.',
      questions: [
        'Top 10 products by revenue as a table',
        'Region vs category cross-tab breakdown',
        'Which products have return rate above average?',
        'Month-over-month revenue trend',
        'Correlation between discount and units sold',
      ],
      metrics: [
        { val: '21.4%', label: 'Return Rate', c: '#ef4444' },
        { val: '3', label: 'Top Revenue Categories', c: '#10b981' },
        { val: '700+', label: 'Orders Analyzed', c: '#8b5cf6' },
      ],
      tag: 'SALES',
      tagColor: '#8b5cf6',
    },
    {
      color: '#f59e0b',
      colorDim: 'rgba(245,158,11,0.12)',
      colorBorder: 'rgba(245,158,11,0.3)',
      icon: '👥',
      domain: 'HR & Workforce Analytics',
      title: 'People Analytics & Attrition Intelligence',
      description:
        'Upload headcount data. Identify employees at attrition risk, compensation outliers, department overstaffing, and diversity gaps — with AI explanations a non-technical HR manager can act on.',
      questions: [
        'Show employees with tenure < 1 year and low rating',
        'Salary distribution by grade and department',
        'Which departments have highest attrition rate?',
        'Cross-tab: gender vs promotion rate',
        'Are there compensation outliers by role?',
      ],
      metrics: [
        { val: '5', label: 'Depts at Attrition Risk', c: '#ef4444' },
        { val: '1.09x', label: 'Gender Pay Gap', c: '#f59e0b' },
        { val: '500', label: 'Employees Tracked', c: '#8b5cf6' },
      ],
      tag: 'PEOPLE',
      tagColor: '#f59e0b',
    },
  ]

  const howItWorks = [
    { step: '01', icon: '📁', title: 'Upload your data', body: 'Drop any Excel (multi-tab) or CSV file. PulseAI handles the rest — no prep, no schema mapping.' },
    { step: '02', icon: '🔍', title: 'AI auto-analyzes', body: 'Schema detection, relationship mapping, KPI extraction, and chart generation happen automatically.' },
    { step: '03', icon: '💬', title: 'Ask in plain English', body: 'Type any question. Get back formatted tables, charts, or AI narratives — no SQL or Python needed.' },
    { step: '04', icon: '📊', title: 'Executive dashboard', body: 'One-click view: KPI cards, AI narrative, 6 chart types, and auto-detected anomalies.' },
    { step: '05', icon: '✅', title: 'Decide with confidence', body: 'Share insights with leadership. Every answer is backed by your actual data, not a model guess.' },
  ]

  return (
    <div className="space-y-8 pb-8">
      {/* Header */}
      <div>
        <div className="flex items-center gap-3 mb-1">
          <span className="text-xs font-bold text-blue-400 uppercase tracking-widest px-3 py-1 rounded-full border border-blue-500/30"
            style={{ background: 'rgba(59,130,246,0.1)' }}>
            USE CASES
          </span>
        </div>
        <h1 className="text-2xl font-bold text-white mt-2">Industry Use Cases</h1>
        <p className="text-gray-400 mt-1 text-sm">
          Real-world scenarios where PulseAI delivers immediate business value — across Banking, Insurance, Retail, and HR.
        </p>
      </div>

      {/* How it works strip */}
      <div className="rounded-2xl p-5 border" style={{ background: 'rgba(255,255,255,0.03)', borderColor: 'rgba(255,255,255,0.08)' }}>
        <p className="text-xs text-gray-500 uppercase tracking-widest font-semibold mb-4">How PulseAI Works</p>
        <div className="grid grid-cols-2 md:grid-cols-5 gap-3">
          {howItWorks.map((s) => (
            <div key={s.step} className="rounded-xl p-3 border relative overflow-hidden"
              style={{ background: 'rgba(15,23,42,0.8)', borderColor: 'rgba(59,130,246,0.15)' }}>
              <div className="text-2xl mb-2">{s.icon}</div>
              <div className="text-xs font-bold text-blue-400 mb-1">{s.step}</div>
              <div className="text-sm font-semibold text-white mb-1">{s.title}</div>
              <div className="text-xs text-gray-500 leading-relaxed">{s.body}</div>
            </div>
          ))}
        </div>
      </div>

      {/* Use Case Cards */}
      <div className="grid grid-cols-1 xl:grid-cols-2 gap-6">
        {cases.map((uc) => (
          <div key={uc.domain} className="rounded-2xl border overflow-hidden"
            style={{ background: 'rgba(15,23,42,0.6)', borderColor: uc.colorBorder }}>

            {/* Top accent bar */}
            <div className="h-1" style={{ background: uc.color }} />

            <div className="p-5">
              {/* Header row */}
              <div className="flex items-start justify-between gap-3 mb-3">
                <div className="flex items-center gap-3">
                  <div className="w-10 h-10 rounded-xl flex items-center justify-center text-2xl shrink-0"
                    style={{ background: uc.colorDim, border: `1px solid ${uc.colorBorder}` }}>
                    {uc.icon}
                  </div>
                  <div>
                    <span className="text-xs font-bold px-2 py-0.5 rounded-full"
                      style={{ background: `${uc.tagColor}22`, color: uc.tagColor, border: `1px solid ${uc.tagColor}44` }}>
                      {uc.tag}
                    </span>
                    <p className="text-xs text-gray-500 mt-0.5">{uc.domain}</p>
                  </div>
                </div>
              </div>

              <h3 className="text-base font-bold text-white mb-2">{uc.title}</h3>
              <p className="text-sm text-gray-400 leading-relaxed mb-4">{uc.description}</p>

              {/* Metrics row */}
              <div className="grid grid-cols-3 gap-2 mb-4">
                {uc.metrics.map((m) => (
                  <div key={m.label} className="rounded-xl p-3 text-center border"
                    style={{ background: 'rgba(0,0,0,0.3)', borderColor: 'rgba(255,255,255,0.06)' }}>
                    <div className="text-lg font-bold" style={{ color: m.c }}>{m.val}</div>
                    <div className="text-xs text-gray-500 mt-0.5 leading-tight">{m.label}</div>
                  </div>
                ))}
              </div>

              {/* Sample questions */}
              <div>
                <p className="text-xs text-gray-600 uppercase tracking-widest font-semibold mb-2">
                  Sample AI Chat Questions
                </p>
                <div className="space-y-1.5">
                  {uc.questions.map((q, i) => (
                    <div key={i} className="flex items-start gap-2 text-xs text-gray-300 rounded-lg px-3 py-2"
                      style={{ background: uc.colorDim, border: `1px solid ${uc.colorBorder}` }}>
                      <span className="shrink-0 font-bold" style={{ color: uc.color }}>→</span>
                      <span>{q}</span>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          </div>
        ))}
      </div>

      {/* Bottom CTA */}
      <div className="rounded-2xl p-6 border text-center"
        style={{ background: 'rgba(59,130,246,0.06)', borderColor: 'rgba(59,130,246,0.2)' }}>
        <p className="text-lg font-bold text-white mb-1">Ready to try it with your data?</p>
        <p className="text-sm text-gray-400 mb-4">
          Upload any Excel or CSV file and get your first insights in under 2 minutes — no setup, no code.
        </p>
        <a href="/sources"
          className="inline-flex items-center gap-2 px-6 py-2.5 bg-blue-600 hover:bg-blue-500 text-white text-sm font-semibold rounded-xl transition-colors">
          Go to Data Sources →
        </a>
      </div>
    </div>
  )
}

export default UseCases
