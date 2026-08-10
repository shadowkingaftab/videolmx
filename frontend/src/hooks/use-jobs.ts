import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { jobsApi, type CrawlJob, type AnalysisJob } from '@/api/jobs'
import { WEBSITES_QUERY_KEY } from './use-website'

export const JOBS_QUERY_KEY = 'jobs'

// Crawl Jobs
export function useCrawlJobs(websiteId?: string, status?: string, page = 1, pageSize = 20) {
  return useQuery({
    queryKey: [JOBS_QUERY_KEY, 'crawl', { websiteId, status, page, pageSize }],
    queryFn: () => jobsApi.listCrawlJobs(websiteId, status, page, pageSize),
  })
}

export function useCrawlJob(jobId: string) {
  return useQuery({
    queryKey: [JOBS_QUERY_KEY, 'crawl', jobId],
    queryFn: () => jobsApi.getCrawlJob(jobId),
    enabled: !!jobId,
  })
}

export function useCreateCrawlJob() {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: ({
      websiteId,
      maxPages = 50,
      depth = 3,
      includeAssets = true,
    }: {
      websiteId: string
      maxPages?: number
      depth?: number
      includeAssets?: boolean
    }) => jobsApi.createCrawlJob(websiteId, maxPages, depth, includeAssets),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: [JOBS_QUERY_KEY] })
      queryClient.invalidateQueries({ queryKey: [WEBSITES_QUERY_KEY] })
    },
  })
}

export function useCancelCrawlJob() {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: (jobId: string) => jobsApi.cancelCrawlJob(jobId),
    onSuccess: (_, jobId) => {
      queryClient.invalidateQueries({ queryKey: [JOBS_QUERY_KEY, 'crawl', jobId] })
      queryClient.invalidateQueries({ queryKey: [JOBS_QUERY_KEY] })
    },
  })
}

export function useCrawlProgress(jobId: string) {
  return useQuery({
    queryKey: [JOBS_QUERY_KEY, 'crawl', jobId, 'progress'],
    queryFn: () => jobsApi.getCrawlProgress(jobId),
    enabled: !!jobId,
    refetchInterval: (data) => {
      const status = data?.status
      if (status === 'running' || status === 'queued') {
        return 2000
      }
      return false
    },
  })
}

// Analysis Jobs
export function useAnalysisJobs(websiteId?: string, status?: string, page = 1, pageSize = 20) {
  return useQuery({
    queryKey: [JOBS_QUERY_KEY, 'analysis', { websiteId, status, page, pageSize }],
    queryFn: () => jobsApi.listAnalysisJobs(websiteId, status, page, pageSize),
  })
}

export function useAnalysisJob(jobId: string) {
  return useQuery({
    queryKey: [JOBS_QUERY_KEY, 'analysis', jobId],
    queryFn: () => jobsApi.getAnalysisJob(jobId),
    enabled: !!jobId,
  })
}

export function useCreateAnalysisJob() {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: ({
      websiteId,
      analysisType = 'full',
      depth = 'standard',
    }: {
      websiteId: string
      analysisType?: string
      depth?: string
    }) => jobsApi.createAnalysisJob(websiteId, analysisType, depth),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: [JOBS_QUERY_KEY] })
      queryClient.invalidateQueries({ queryKey: [WEBSITES_QUERY_KEY] })
    },
  })
}

export function useCancelAnalysisJob() {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: (jobId: string) => jobsApi.cancelAnalysisJob(jobId),
    onSuccess: (_, jobId) => {
      queryClient.invalidateQueries({ queryKey: [JOBS_QUERY_KEY, 'analysis', jobId] })
      queryClient.invalidateQueries({ queryKey: [JOBS_QUERY_KEY] })
    },
  })
}

export function useAnalysisProgress(jobId: string) {
  return useQuery({
    queryKey: [JOBS_QUERY_KEY, 'analysis', jobId, 'progress'],
    queryFn: () => jobsApi.getAnalysisProgress(jobId),
    enabled: !!jobId,
    refetchInterval: (data) => {
      const status = data?.status
      if (status === 'running' || status === 'pending') {
        return 2000
      }
      return false
    },
  })
}

// Generic job hook
export function useJob(jobId: string) {
  return useQuery({
    queryKey: [JOBS_QUERY_KEY, jobId],
    queryFn: async () => {
      // Try to fetch as crawl job first
      try {
        return await jobsApi.getCrawlJob(jobId)
      } catch {
        // Fall back to analysis job
        return await jobsApi.getAnalysisJob(jobId)
      }
    },
    enabled: !!jobId,
  })
}