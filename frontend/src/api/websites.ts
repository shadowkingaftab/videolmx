import apiClient from './client'

export interface Website {
  id: string
  project_id: string
  url: string
  title?: string
  description?: string
  status: 'pending' | 'crawling' | 'analyzing' | 'completed' | 'failed'
  crawled_at?: string
  analyzed_at?: string
  digital_twin?: Record<string, any>
  created_at: string
  updated_at: string
}

export interface CreateWebsiteRequest {
  project_id: string
  url: string
}

export interface UpdateWebsiteRequest {
  title?: string
  description?: string
  status?: string
}

export const websitesApi = {
  list: async (projectId?: string, page = 1, pageSize = 20) => {
    const params = new URLSearchParams({
      page: String(page),
      page_size: String(pageSize),
      ...(projectId && { project_id: projectId }),
    })
    const response = await apiClient.get(`/api/v1/websites?${params}`)
    return response.data
  },

  create: async (data: CreateWebsiteRequest): Promise<Website> => {
    const response = await apiClient.post('/api/v1/websites', data)
    return response.data
  },

  get: async (websiteId: string): Promise<Website> => {
    const response = await apiClient.get(`/api/v1/websites/${websiteId}`)
    return response.data
  },

  update: async (websiteId: string, data: UpdateWebsiteRequest): Promise<Website> => {
    const response = await apiClient.patch(`/api/v1/websites/${websiteId}`, data)
    return response.data
  },

  delete: async (websiteId: string): Promise<void> => {
    await apiClient.delete(`/api/v1/websites/${websiteId}`)
  },

  analyze: async (websiteId: string, maxPages = 50, depth = 3, includeAssets = true) => {
    const response = await apiClient.post(`/api/v1/websites/${websiteId}/analyze`, {
      max_pages: maxPages,
      depth,
      include_assets: includeAssets,
    })
    return response.data
  },

  getAnalysisStatus: async (websiteId: string) => {
    const response = await apiClient.get(`/api/v1/websites/${websiteId}/analyze/status`)
    return response.data
  },

  getPages: async (websiteId: string, page = 1, pageSize = 20) => {
    const params = new URLSearchParams({
      page: String(page),
      page_size: String(pageSize),
    })
    const response = await apiClient.get(`/api/v1/websites/${websiteId}/pages?${params}`)
    return response.data
  },

  getAssets: async (websiteId: string, assetType?: string, page = 1, pageSize = 20) => {
    const params = new URLSearchParams({
      page: String(page),
      page_size: String(pageSize),
      ...(assetType && { asset_type: assetType }),
    })
    const response = await apiClient.get(`/api/v1/websites/${websiteId}/assets?${params}`)
    return response.data
  },

  getDigitalTwin: async (websiteId: string) => {
    const response = await apiClient.get(`/api/v1/websites/${websiteId}/digital-twin`)
    return response.data
  },
}