import apiClient from './client'

export interface Export {
  id: string
  video_id: string
  format: 'mp4' | 'webm' | 'gif' | 'avi' | 'mov'
  quality: 'low' | 'medium' | 'high'
  status: 'pending' | 'exporting' | 'completed' | 'failed'
  progress: number
  include_watermark: boolean
  include_metadata: boolean
  file_size?: number
  file_url?: string
  storage_key?: string
  download_count: number
  started_at?: string
  completed_at?: string
  expires_at?: string
  error_message?: string
  created_at: string
  updated_at: string
}

export interface CreateExportRequest {
  video_id: string
  format: 'mp4' | 'webm' | 'gif' | 'avi' | 'mov'
  quality?: 'low' | 'medium' | 'high'
  include_watermark?: boolean
}

export interface UpdateExportRequest {
  status?: string
  progress?: number
  file_size?: number
  file_url?: string
  storage_key?: string
  error_message?: string
}

export const exportsApi = {
  list: async (videoId?: string, status?: string, page = 1, pageSize = 20) => {
    const params = new URLSearchParams({
      page: String(page),
      page_size: String(pageSize),
      ...(videoId && { video_id: videoId }),
      ...(status && { status }),
    })
    const response = await apiClient.get(`/api/v1/exports?${params}`)
    return response.data
  },

  create: async (data: CreateExportRequest): Promise<Export> => {
    const response = await apiClient.post('/api/v1/exports', data)
    return response.data
  },

  get: async (exportId: string): Promise<Export> => {
    const response = await apiClient.get(`/api/v1/exports/${exportId}`)
    return response.data
  },

  update: async (exportId: string, data: UpdateExportRequest): Promise<Export> => {
    const response = await apiClient.patch(`/api/v1/exports/${exportId}`, data)
    return response.data
  },

  delete: async (exportId: string): Promise<void> => {
    await apiClient.delete(`/api/v1/exports/${exportId}`)
  },

  getDownloadUrl: async (exportId: string) => {
    const response = await apiClient.get(`/api/v1/exports/${exportId}/download`)
    return response.data
  },

  getStatus: async (exportId: string) => {
    const response = await apiClient.get(`/api/v1/exports/${exportId}/status`)
    return response.data
  },

  retry: async (exportId: string) => {
    const response = await apiClient.post(`/api/v1/exports/${exportId}/retry`)
    return response.data
  },

  getFormats: async () => {
    const response = await apiClient.get('/api/v1/exports/formats')
    return response.data
  },
}