import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { videosApi, type Video, type CreateVideoRequest, type RenderVideoRequest } from '@/api/videos'
import { PROJECTS_QUERY_KEY } from './use-projects'

export const VIDEOS_QUERY_KEY = 'videos'

export function useVideos(projectId?: string, status?: string, page = 1, pageSize = 20) {
  return useQuery({
    queryKey: [VIDEOS_QUERY_KEY, { projectId, status, page, pageSize }],
    queryFn: () => videosApi.list(projectId, status, page, pageSize),
  })
}

export function useVideo(videoId: string) {
  return useQuery({
    queryKey: [VIDEOS_QUERY_KEY, videoId],
    queryFn: () => videosApi.get(videoId),
    enabled: !!videoId,
  })
}

export function useCreateVideo() {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: (data: CreateVideoRequest) => videosApi.create(data),
    onSuccess: (data) => {
      queryClient.invalidateQueries({ queryKey: [VIDEOS_QUERY_KEY] })
      queryClient.invalidateQueries({
        queryKey: [PROJECTS_QUERY_KEY, data.project_id, 'videos'],
      })
    },
  })
}

export function useUpdateVideo() {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: ({ videoId, data }: { videoId: string; data: Partial<Video> }) =>
      videosApi.update(videoId, data),
    onSuccess: (_, { videoId }) => {
      queryClient.invalidateQueries({ queryKey: [VIDEOS_QUERY_KEY, videoId] })
      queryClient.invalidateQueries({ queryKey: [VIDEOS_QUERY_KEY] })
    },
  })
}

export function useDeleteVideo() {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: (videoId: string) => videosApi.delete(videoId),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: [VIDEOS_QUERY_KEY] })
    },
  })
}

export function useRenderVideo() {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: ({ videoId, data }: { videoId: string; data: RenderVideoRequest }) =>
      videosApi.render(videoId, data),
    onSuccess: (_, { videoId }) => {
      queryClient.invalidateQueries({ queryKey: [VIDEOS_QUERY_KEY, videoId] })
    },
  })
}

export function useVideoStatus(videoId: string) {
  return useQuery({
    queryKey: [VIDEOS_QUERY_KEY, videoId, 'status'],
    queryFn: () => videosApi.getStatus(videoId),
    enabled: !!videoId,
    refetchInterval: (data) => {
      const status = data?.status
      if (status === 'rendering' || status === 'generating') {
        return 3000
      }
      return false
    },
  })
}

export function useExports(videoId: string) {
  return useQuery({
    queryKey: [VIDEOS_QUERY_KEY, videoId, 'exports'],
    queryFn: () => videosApi.listExports(videoId),
    enabled: !!videoId,
  })
}

export function useExportVideo() {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: ({ videoId, data }: { videoId: string; data: any }) =>
      videosApi.export(videoId, data),
    onSuccess: (_, { videoId }) => {
      queryClient.invalidateQueries({ queryKey: [VIDEOS_QUERY_KEY, videoId, 'exports'] })
    },
  })
}

export function useVideoDownloadUrl(videoId: string) {
  return useQuery({
    queryKey: [VIDEOS_QUERY_KEY, videoId, 'download'],
    queryFn: () => videosApi.getDownloadUrl(videoId),
    enabled: !!videoId,
  })
}