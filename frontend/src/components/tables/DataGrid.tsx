import { useMemo } from 'react'

interface ColDef {
  field: string
  sortable: boolean
  filter: boolean
  resizable: boolean
}

interface DataGridProps {
  rowData: Record<string, unknown>[]
  className?: string
}

export default function DataGrid({ rowData, className = '' }: DataGridProps) {
  const columnDefs: ColDef[] = useMemo(() => {
    if (!rowData?.length) return []
    return Object.keys(rowData[0]).map((field) => ({
      field,
      sortable: true,
      filter: true,
      resizable: true,
    }))
  }, [rowData])

  if (!rowData?.length) {
    return (
      <div className={`flex items-center justify-center h-40 bg-gray-50 rounded-lg border border-gray-200 text-gray-400 ${className}`}>
        No data available
      </div>
    )
  }

  return (
    <div className={`overflow-auto rounded-lg border border-gray-200 ${className}`}>
      <table className="w-full text-sm text-left">
        <thead className="bg-gray-50 text-gray-600 uppercase text-xs">
          <tr>
            {columnDefs.map((col) => (
              <th key={col.field} className="px-4 py-3 font-medium">{col.field}</th>
            ))}
          </tr>
        </thead>
        <tbody className="divide-y divide-gray-100">
          {rowData.slice(0, 100).map((row, i) => (
            <tr key={i} className="hover:bg-gray-50">
              {columnDefs.map((col) => (
                <td key={col.field} className="px-4 py-2 text-gray-700">
                  {String(row[col.field] ?? '')}
                </td>
              ))}
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  )
}
