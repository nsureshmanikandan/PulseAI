import { useCallback, useEffect, useState } from 'react'
import { useAppStore } from '../store/useAppStore'

interface Dataset {
  id: string
  name: string
  status: string
  tab_names?: string
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

  const selectDataset = useCallback((dataset: Dataset) => {
    // Parse tab_names from JSON string if needed
    let tabNames: string[] = []
    try {
      tabNames = JSON.parse(dataset.tab_names || '[]')
    } catch {
      tabNames = []
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
