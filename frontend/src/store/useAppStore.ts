import { create } from 'zustand'

export interface TabProfile {
  tabName: string
  rowCount: number
  columnProfiles: Record<string, { type: string; nullPct: number; uniqueCount: number }>
}

export interface Dataset {
  id: string
  name: string
  tabNames: string[]
  tabs: TabProfile[]
  createdAt: string
}

export interface ChatMessage {
  id: string
  role: 'user' | 'assistant'
  content: string
  chartConfig?: object
  timestamp: string
}

interface AppStore {
  activeDataset: Dataset | null
  datasets: Dataset[]
  view: 'executive' | 'analyst'
  activeTab: string | null
  chatMessages: ChatMessage[]
  setActiveDataset: (dataset: Dataset | null) => void
  setDatasets: (datasets: Dataset[]) => void
  setView: (view: 'executive' | 'analyst') => void
  setActiveTab: (tab: string | null) => void
  addChatMessage: (msg: ChatMessage) => void
  clearChat: () => void
}

export const useAppStore = create<AppStore>((set) => ({
  activeDataset: null,
  datasets: [],
  view: 'executive',
  activeTab: null,
  chatMessages: [],
  setActiveDataset: (dataset) => set({ activeDataset: dataset, activeTab: dataset?.tabNames[0] ?? null }),
  setDatasets: (datasets) => set({ datasets }),
  setView: (view) => set({ view }),
  setActiveTab: (tab) => set({ activeTab: tab }),
  addChatMessage: (msg) => set((s) => ({ chatMessages: [...s.chatMessages, msg] })),
  clearChat: () => set({ chatMessages: [] }),
}))
