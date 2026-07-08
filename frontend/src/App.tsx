import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom'
import { Sidebar } from './components/layout/Sidebar'
import { TopBar } from './components/layout/TopBar'
import { ExecutiveDashboard } from './pages/ExecutiveDashboard'
import { AnalystWorkbench } from './pages/AnalystWorkbench'
import { AIChat } from './pages/AIChat'
import { DataSources } from './pages/DataSources'
import { UseCases } from './pages/UseCases'
import { ROIBenefits } from './pages/ROIBenefits'

export default function App() {
  return (
    <BrowserRouter>
      <div className="flex h-screen overflow-hidden" style={{ background: '#0a0f1e' }}>
        <Sidebar />
        <div className="flex flex-col flex-1 overflow-hidden">
          <TopBar />
          <main className="flex-1 overflow-auto p-6">
            <Routes>
              <Route path="/" element={<Navigate to="/executive" replace />} />
              <Route path="/executive" element={<ExecutiveDashboard />} />
              <Route path="/analyst" element={<AnalystWorkbench />} />
              <Route path="/chat" element={<AIChat />} />
              <Route path="/sources" element={<DataSources />} />
              <Route path="/usecases" element={<UseCases />} />
              <Route path="/roi" element={<ROIBenefits />} />
            </Routes>
          </main>
        </div>
      </div>
    </BrowserRouter>
  )
}
