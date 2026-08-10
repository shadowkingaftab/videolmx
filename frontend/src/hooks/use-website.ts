import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { websitesApi, type Website, type CreateWebsiteRequest } from '@/api/websites'
import { PROJECTS_QUERY_KEY } from './use-projects'

export const WEBSITES_QUERY_KEY = 'websites'

export function useWebsites(projectId?: string, page = 1, pageSize = 20) {
  return useQuery({
    queryKey: [WEBSITES_QUERY_KEY, { projectId, page, pageSize }],
    queryFn: () => websitesApi.list(projectId, page, pageSize),
  })
}

export function useWebsite(websiteId: string) {
  return useQuery({
    queryKey: [WEBSITES_QUERY_KEY, websiteId],
    queryFn: () => websitesApi.get(websiteId),
    enabled: !!websiteId,
  })
}

export function useCreateWebsite() {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: (data: CreateWebsiteRequest) => websitesApi.create(data),
    onSuccess: (data) => {
      queryClient.invalidateQueries({ queryKey: [WEBSITES_QUERY_KEY] })
      queryClient.invalidateQueries({
        queryKey: [PROJECTS_QUERY_KEY, data.project_id, 'websites'],
      })
    },
  })
}

export function useUpdateWebsite() {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: ({ websiteId, data }: { websiteId: string; data: Partial<Website> }) =>
      websitesApi.update(websiteId, data),
    onSuccess: (_, { websiteId }) => {
      queryClient.invalidateQueries({ queryKey: [WEBSITES_QUERY_KEY, websiteId] })
      queryClient.invalidateQueries({ queryKey: [WEBSITES_QUERY_KEY] })
    },
  })
}

export function useDeleteWebsite() {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: (websiteId: string) => websitesApi.delete(websiteId),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: [WEBSITES_QUERY_KEY] })
    },
  })
}

export function useAnalyzeWebsite() {
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
    }) => websitesApi.analyze(websiteId, maxPages, depth, includeAssets),
    onSuccess: (_, { websiteId }) => {
      queryClient.invalidateQueries({ queryKey: [WEBSITES_QUERY_KEY, websiteId] })
    },
  })
}

export function useWebsiteAnalysisStatus(websiteId: string) {
  return useQuery({
    queryKey: [WEBSITES_QUERY_KEY, websiteId, 'analysis-status'],
    queryFn: () => websitesApi.getAnalysisStatus(websiteId),
    enabled: !!websiteId,
    refetchInterval: (data) => {
      const status = data?.status
      if (status === 'running' || status === 'pending') {
        return 3000 // Poll every 3 seconds when running
      }
      return false
    },
  })
}

export function useWebsitePages(websiteId: string, page = 1, pageSize = 20) {
  return useQuery({
    queryKey: [WEBSITES_QUERY_KEY, websiteId, 'pages', { page, pageSize }],
    queryFn: () => websitesApi.getPages(websiteId, page, pageSize),
    enabled: !!websiteId,
  })
}

export function useWebsiteAssets(
  websiteId: string,
  assetType?: string,
  page = 1,
  pageSize = 20
) {
  return useQuery({
    queryKey: [WEBSITES_QUERY_KEY, websiteId, 'assets', { assetType, page, pageSize }],
    queryFn: () => websitesApi.getAssets(websiteId, assetType, page, pageSize),
    enabled: !!websiteId,
  })
}

export function useWebsiteDigitalTwin(websiteId: string) {
  return useQuery({
    queryKey: [WEBSITES_QUERY_KEY, websiteId, 'digital-twin'],
    queryFn: () => websitesApi.getDigitalTwin(websiteId),
    enabled: !!websiteId,
  })
}