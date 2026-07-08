/**
 * Self-healing hook: if a dataset is selected but activeTab is null
 * (because tab_names was empty at selection time), re-fetch the dataset
 * from the API to get the real tab list and restore activeTab.
 */
import { useEffect } from 'react'
import { useAppStore } from '../store/useAppStore'

export function useHealActiveTab() {
  const activeDataset   = useAppStore((s) => s.activeDataset)
  const activeTab       = useAppStore((s) => s.activeTab)
  const setActiveDataset = useAppStore((s) => s.setActiveDataset)

  useEffect(() => {
    if (!activeDataset || activeTab) return   // nothing to heal
    fetch(`/api/datasets/${activeDataset.id}`)
      .then(r => r.json())
      .then(fresh => {
        const tabs: string[] = Array.isArray(fresh.tab_names) ? fresh.tab_names : []
        if (tabs.length > 0) {
          setActiveDataset({ ...activeDataset, tabNames: tabs })
        }
      })
      .catch(() => {})
  }, [activeDataset?.id, activeTab])
}
