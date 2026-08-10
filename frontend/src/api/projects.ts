import apiClient from './client'

export interface Project {
  id: string
  user_id: string
  name: string
  description?: string
  status: 'active' | 'archived' | 'deleted'
  settings?: Record<string, any>
  created_at: string
  updated_at: string
  video_count?: number
  website_count?: number
}

export interface CreateProjectRequest {
  name: string
  description?: string
}

export interface UpdateProjectRequest {
  name?: string
  description?: string
  status?: string
}

export const projectsApi = {
  list: async (page = 1, pageSize = 20, status?: string) => {
    const params = new URLSearchParams({
      page: String(page),
      page_size: String(pageSize),
      ...(status && { status }),
    })
    const response = await apiClient.get(`/api/v1/projects?${params}`)
    return response.data
  },

  create: async (data: CreateProjectRequest): Promise<Project> => {
    const response = await apiClient.post('/api/v1/projects', data)
    return response.data
  },

  get: async (projectId: string): Promise<Project> => {
    const response = await apiClient.get(`/api/v1/projects/${projectId}`)
    return response.data
  },

  update: async (projectId: string, data: UpdateProjectRequest): Promise<Project> => {
    const response = await apiClient.patch(`/api/v1/projects/${projectId}`, data)
    return response.data
  },

  delete: async (projectId: string): Promise<void> => {
    await apiClient.delete(`/api/v1/projects/${projectId}`)
  },

  archive: async (projectId: string): Promise<void> => {
    await apiClient.post(`/api/v1/projects/${projectId}/archive`)
  },

  restore: async (projectId: string): Promise<void> => {
    await apiClient.post(`/api/v1/projects/${projectId}/restore`)
  },

  getStats: async (projectId: string) => {
    const response = await apiClient.get(`/api/v1/projects/${projectId}/stats`)
    return response.data
  },

  getWebsites: async (projectId: string, page = 1, pageSize = 20) => {
    const params = new URLSearchParams({
      page: String(page),
      page_size: String(pageSize),
    })
    const response = await apiClient.get(`/api/v1/projects/${projectId}/websites?${params}`)
    return response.data
  },

  getVideos: async (projectId: string, page = 1, pageSize = 20) => {
    const params = new URLSearchParams({
      page: String(page),
      page_size: String(pageSize),
    })
    const response = await apiClient.get(`/api/v1/projects/${projectId}/videos?${params}`)
    return response.data
  },
}