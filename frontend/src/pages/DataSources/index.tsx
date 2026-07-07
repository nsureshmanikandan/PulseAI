import { useRef } from 'react'
import { useDataset } from '../../hooks/useDataset'
import { useAppStore } from '../../store/useAppStore'

export function DataSources() {
  const { datasets, loading, uploading, error, uploadDataset, deleteDataset, selectDataset } = useDataset()
  const activeDataset = useAppStore((s) => s.activeDataset)
  const fileInputRef = useRef<HTMLInputElement>(null)

  const handleFileChange = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0]
    if (!file) return
    await uploadDataset(file)
    if (fileInputRef.current) fileInputRef.current.value = ''
  }

  const statusBadge = (status: string) => {
    const styles: Record<string, string> = {
      completed: 'bg-green-100 text-green-700',
      processing: 'bg-yellow-100 text-yellow-700',
      failed: 'bg-red-100 text-red-700',
    }
    return (
      <span className={`text-xs px-2 py-0.5 rounded-full font-medium ${styles[status] || 'bg-gray-100 text-gray-600'}`}>
        {status}
      </span>
    )
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-bold text-gray-900">Data Sources</h2>
          <p className="text-sm text-gray-500 mt-1">Upload Excel files to analyze</p>
        </div>
        <div>
          <input
            ref={fileInputRef}
            type="file"
            accept=".xlsx,.xls"
            onChange={handleFileChange}
            className="hidden"
            id="file-upload"
          />
          <label
            htmlFor="file-upload"
            className={`cursor-pointer px-4 py-2 bg-blue-600 text-white text-sm font-medium rounded-lg hover:bg-blue-700 transition-colors ${uploading ? 'opacity-50 pointer-events-none' : ''}`}
          >
            {uploading ? 'Uploading...' : '+ Upload Excel File'}
          </label>
        </div>
      </div>

      {error && (
        <div className="bg-red-50 border border-red-200 text-red-700 rounded-lg px-4 py-3 text-sm">{error}</div>
      )}

      {loading ? (
        <div className="space-y-3">
          {[1, 2, 3].map((i) => (
            <div key={i} className="bg-white rounded-xl border border-gray-200 p-4 animate-pulse">
              <div className="h-4 bg-gray-200 rounded w-1/3 mb-2" />
              <div className="h-3 bg-gray-100 rounded w-1/4" />
            </div>
          ))}
        </div>
      ) : datasets.length === 0 ? (
        <div className="flex flex-col items-center justify-center bg-white rounded-xl border-2 border-dashed border-gray-300 py-16 text-gray-400">
          <span className="text-5xl mb-4">📂</span>
          <p className="font-medium">No datasets yet</p>
          <p className="text-sm mt-1">Upload an Excel file to get started</p>
        </div>
      ) : (
        <div className="space-y-3">
          {datasets.map((ds) => {
            const isActive = activeDataset?.id === ds.id
            return (
              <div
                key={ds.id}
                className={`bg-white rounded-xl border p-4 flex items-center justify-between transition-all ${
                  isActive ? 'border-blue-400 shadow-sm ring-1 ring-blue-200' : 'border-gray-200 hover:border-gray-300'
                }`}
              >
                <div className="flex items-center gap-3 flex-1 min-w-0">
                  <span className="text-2xl">📊</span>
                  <div className="min-w-0">
                    <p className="font-medium text-gray-900 truncate">{ds.name}</p>
                    <div className="flex items-center gap-2 mt-1">
                      {statusBadge(ds.status)}
                      {ds.row_count !== undefined && (
                        <span className="text-xs text-gray-400">{ds.row_count.toLocaleString()} rows</span>
                      )}
                    </div>
                  </div>
                </div>
                <div className="flex items-center gap-2 ml-4">
                  <button
                    onClick={() => selectDataset(ds)}
                    disabled={ds.status !== 'completed'}
                    className="px-3 py-1 text-sm font-medium bg-blue-50 text-blue-700 rounded-lg hover:bg-blue-100 disabled:opacity-40 disabled:cursor-not-allowed transition-colors"
                  >
                    {isActive ? '✓ Active' : 'Select'}
                  </button>
                  <button
                    onClick={() => deleteDataset(ds.id)}
                    className="px-3 py-1 text-sm font-medium bg-red-50 text-red-600 rounded-lg hover:bg-red-100 transition-colors"
                  >
                    Delete
                  </button>
                </div>
              </div>
            )
          })}
        </div>
      )}
    </div>
  )
}
