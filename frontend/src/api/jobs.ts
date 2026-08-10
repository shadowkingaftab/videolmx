import apiClient from './client'

export interface Job {
  id: string
  type: string
  status: 'pending' | 'queued' | 'running' | 'completed' | 'failed' | 'cancelled'
  progress: number
  error_message?: string
  started_at?: string
  completed_at?: string
  created_at: string
  results?: Record<string, any>
}

export interface CrawlJob extends Job {
  website_id: string
  max_pages: number
  max_depth: number
  include_assets: boolean
  pages_crawled: number
  total_pages: number
  assets_collected: number
}

export interface AnalysisJob extends Job {
  website_id: string
  analysis_type: string
  depth: string
  summary?: string
}

export const jobsApi = {
  // Crawl Jobs
  listCrawlJobs: async (websiteId?: string, status?: string, page = 1, pageSize = 20) => {
    const params = new URLSearchParams({
      page: String(page),
      page_size: String(pageSize),
      ...(websiteId && { website_id: websiteId }),
      ...(status && { status }),
    })
    const response = await apiClient.get(`/api/v1/crawl-jobs?${params}`)
    return response.data
  },

  getCrawlJob: async (jobId: string): Promise<CrawlJob> => {
    const response = await apiClient.get(`/api/v1/crawl-jobs/${jobId}`)
    return response.data
  },

  createCrawlJob: async (websiteId: string, maxPages = 50, depth = 3, includeAssets = true) => {
    const response = await apiClient.post('/api/v1/crawl-jobs', {
      website_id: websiteId,
      max_pages: maxPages,
      depth,
      include_assets: includeAssets,
    })
    return response.data
  },

  cancelCrawlJob: async (jobId: string): Promise<void> => {
    await apiClient.post(`/api/v1/crawl-jobs/${jobId}/cancel`)
  },

  getCrawlProgress: async (jobId: string) => {
    const response = await apiClient.get(`/api/v1/crawl-jobs/${jobId}/progress`)
    return response.data
  },

  getCrawlResults: async (jobId: string) => {
    const response = await apiClient.get(`/api/v1/crawl-jobs/${jobId}/results`)
    return response.data
  },

  // Analysis Jobs
  listAnalysisJobs: async (websiteId?: string, status?: string, page = 1, pageSize = 20) => {
    const params = new URLSearchParams({
      page: String(page),
      page_size: String(pageSize),
      ...(websiteId && { website_id: websiteId }),
      ...(status && { status }),
    })
    const response = await apiClient.get(`/api/v1/analysis-jobs?${params}`)
    return response.data
  },

  getAnalysisJob: async (jobId: string): Promise<AnalysisJob> => {
    const response = await apiClient.get(`/api/v1/analysis-jobs/${jobId}`)
    return response.data
  },

  createAnalysisJob: async (websiteId: string, analysisType = 'full', depth = 'standard') => {
    const response = await apiClient.post('/api/v1/analysis-jobs', {
      website_id: websiteId,
      analysis_type: analysisType,
      depth,
    })
    return response.data
  },

  cancelAnalysisJob: async (jobId: string): Promise<void> => {
    await apiClient.post(`/api/v1/analysis-jobs/${jobId}/cancel`)
  },

  getAnalysisProgress: async (jobId: string) => {
    const response = await apiClient.get(`/api/v1/analysis-jobs/${jobId}/progress`)
    return response.data
  },

  getAnalysisResults: async (jobId: string) => {
    const response = await apiClient.get(`/api/v1/analysis-jobs/${jobId}/results`)
    return response.data
  },

  getAnalysisInsights: async (jobId: string) => {
    const response = await apiClient.get(`/api/v1/analysis-jobs/${jobId}/insights`)
    return response.data
  },
}