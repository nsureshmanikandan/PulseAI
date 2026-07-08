import { useCallback, useEffect, useState } from 'react'
import { useAppStore } from '../store/useAppStore'

interface Dataset {
  id: string
  name: string
  status: string
  tab_names?: string | string[]
  row_count?: number
}

export function useDataset() {
  const setActiveDataset = useAppStore((s) => s.setActiveDataset)
  const [datasets, setDatasets] = useState<Dataset[]>([])
  const [loading, setLoading] = useState(false)
  const [uploading, setUploading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const fetchDatasets = useCallback(async () => {
    setLoading(true)
    try {
      const res = await fetch('/api/datasets/')
      if (!res.ok) throw new Error('Failed to fetch datasets')
      const data = await res.json()
      setDatasets(data)
    } catch (e) {
      setError((e as Error).message)
    } finally {
      setLoading(false)
    }
  }, [])

  useEffect(() => {
    fetchDatasets()
  }, [fetchDatasets])

  const uploadDataset = useCallback(async (file: File): Promise<boolean> => {
    setUploading(true)
    setError(null)
    try {
      const form = new FormData()
      form.append('file', file)
      const res = await fetch('/api/datasets/upload', { method: 'POST', body: form })
      if (!res.ok) {
        const err = await res.json()
        throw new Error(err.detail || 'Upload failed')
      }
      await fetchDatasets()
      return true
    } catch (e) {
      setError((e as Error).message)
      return false
    } finally {
      setUploading(false)
    }
  }, [fetchDatasets])

  const deleteDataset = useCallback(async (id: string) => {
    try {
      await fetch(`/api/datasets/${id}`, { method: 'DELETE' })
      setDatasets((prev) => prev.filter((d) => d.id !== id))
    } catch {
      setError('Failed to delete dataset')
    }
  }, [])

  const selectDataset = useCallback(async (dataset: Dataset) => {
    // Re-fetch the dataset from API to get up-to-date tab_names after processing
    let tabNames: string[] = []
    try {
      const res = await fetch(`/api/datasets/${dataset.id}`)
      if (res.ok) {
        const fresh = await res.json()
        const raw = fresh.tab_names
        if (Array.isArray(raw)) tabNames = raw
        else if (typeof raw === 'string' && raw) {
          try { tabNames = JSON.parse(raw) } catch { tabNames = [raw] }
        }
      }
    } catch { /* fall through to stale data */ }

    // Fallback to stale tab_names from list if re-fetch failed
    if (tabNames.length === 0) {
      const raw = dataset.tab_names
      if (Array.isArray(raw)) tabNames = raw as string[]
      else if (typeof raw === 'string' && raw) {
        try { tabNames = JSON.parse(raw) } catch { tabNames = [raw] }
      }
    }

    setActiveDataset({
      id: dataset.id,
      name: dataset.name,
      tabNames,
      tabs: [],
      createdAt: new Date().toISOString(),
    })
  }, [setActiveDataset])

  return { datasets, loading, uploading, error, uploadDataset, deleteDataset, selectDataset, refetch: fetchDatasets }
}
