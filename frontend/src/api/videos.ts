import apiClient from './client'

export interface Video {
  id: string
  project_id: string
  name: string
  description?: string
  storyboard_id?: string
  script_id?: string
  narration_id?: string
  status: 'draft' | 'generating' | 'rendering' | 'ready' | 'failed'
  progress: number
  resolution: string
  fps: number
  quality: string
  duration?: number
  file_size?: number
  file_url?: string
  preview_url?: string
  thumbnail_url?: string
  render_started_at?: string
  render_completed_at?: string
  error_message?: string
  created_at: string
  updated_at: string
}

export interface CreateVideoRequest {
  project_id: string
  name: string
  description?: string
  storyboard_id?: string
  script_id?: string
  narration_id?: string
}

export interface UpdateVideoRequest {
  name?: string
  description?: string
  status?: string
  resolution?: string
  fps?: number
  quality?: string
}

export interface RenderVideoRequest {
  resolution?: string
  fps?: number
  quality?: string
  include_captions?: boolean
  include_background_music?: boolean
}

export interface ExportVideoRequest {
  format: 'mp4' | 'webm' | 'gif' | 'avi' | 'mov'
  quality?: 'low' | 'medium' | 'high'
  include_watermark?: boolean
}

export const videosApi = {
  list: async (projectId?: string, status?: string, page = 1, pageSize = 20) => {
    const params = new URLSearchParams({
      page: String(page),
      page_size: String(pageSize),
      ...(projectId && { project_id: projectId }),
      ...(status && { status }),
    })
    const response = await apiClient.get(`/api/v1/videos?${params}`)
    return response.data
  },

  create: async (data: CreateVideoRequest): Promise<Video> => {
    const response = await apiClient.post('/api/v1/videos', data)
    return response.data
  },

  get: async (videoId: string): Promise<Video> => {
    const response = await apiClient.get(`/api/v1/videos/${videoId}`)
    return response.data
  },

  update: async (videoId: string, data: UpdateVideoRequest): Promise<Video> => {
    const response = await apiClient.patch(`/api/v1/videos/${videoId}`, data)
    return response.data
  },

  delete: async (videoId: string): Promise<void> => {
    await apiClient.delete(`/api/v1/videos/${videoId}`)
  },

  render: async (videoId: string, data: RenderVideoRequest) => {
    const response = await apiClient.post(`/api/v1/videos/${videoId}/render`, data)
    return response.data
  },

  getStatus: async (videoId: string) => {
    const response = await apiClient.get(`/api/v1/videos/${videoId}/status`)
    return response.data
  },

  getDownloadUrl: async (videoId: string) => {
    const response = await apiClient.get(`/api/v1/videos/${videoId}/download`)
    return response.data
  },

  getStreamUrl: async (videoId: string) => {
    const response = await apiClient.get(`/api/v1/videos/${videoId}/stream`)
    return response.data
  },

  export: async (videoId: string, data: ExportVideoRequest) => {
    const response = await apiClient.post(`/api/v1/videos/${videoId}/export`, data)
    return response.data
  },

  listExports: async (videoId: string) => {
    const response = await apiClient.get(`/api/v1/videos/${videoId}/exports`)
    return response.data
  },
}