import axios from 'axios'

const api = axios.create({
  baseURL: import.meta.env.VITE_API_URL ?? 'http://localhost:8000',
  timeout: 30000,
})

api.interceptors.response.use(
  (res) => res,
  (err) => {
    const message = err.response?.data?.detail ?? 'An error occurred'
    return Promise.reject(new Error(message))
  }
)

export const datasetsApi = {
  list: () => api.get('/api/datasets'),
  upload: (file: File) => {
    const form = new FormData()
    form.append('file', file)
    return api.post('/api/datasets/upload', form)
  },
  get: (id: string) => api.get(`/api/datasets/${id}`),
  delete: (id: string) => api.delete(`/api/datasets/${id}`),
}

export const analyticsApi = {
  kpis: (datasetId: string) => api.get(`/api/analytics/kpis/${datasetId}`),
  stats: (datasetId: string, tabName: string) => api.get(`/api/analytics/stats/${datasetId}/${tabName}`),
  chart: (datasetId: string, payload: object) => api.post(`/api/analytics/chart/${datasetId}`, payload),
  relationships: (datasetId: string) => api.get(`/api/analytics/relationships/${datasetId}`),
}

export const aiApi = {
  narrative: (datasetId: string) => api.get(`/api/ai/narrative/${datasetId}`),
  insights: (datasetId: string) => api.get(`/api/ai/insights/${datasetId}`),
  saveQuery: (payload: object) => api.post('/api/ai/save-query', payload),
}

export default api
