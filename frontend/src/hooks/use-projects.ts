import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { projectsApi, type Project, type CreateProjectRequest } from '@/api/projects'

export const PROJECTS_QUERY_KEY = 'projects'

export function useProjects(page = 1, pageSize = 20, status?: string) {
  return useQuery({
    queryKey: [PROJECTS_QUERY_KEY, { page, pageSize, status }],
    queryFn: () => projectsApi.list(page, pageSize, status),
  })
}

export function useProject(projectId: string) {
  return useQuery({
    queryKey: [PROJECTS_QUERY_KEY, projectId],
    queryFn: () => projectsApi.get(projectId),
    enabled: !!projectId,
  })
}

export function useCreateProject() {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: (data: CreateProjectRequest) => projectsApi.create(data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: [PROJECTS_QUERY_KEY] })
    },
  })
}

export function useUpdateProject() {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: ({ projectId, data }: { projectId: string; data: Partial<Project> }) =>
      projectsApi.update(projectId, data),
    onSuccess: (_, { projectId }) => {
      queryClient.invalidateQueries({ queryKey: [PROJECTS_QUERY_KEY, projectId] })
      queryClient.invalidateQueries({ queryKey: [PROJECTS_QUERY_KEY] })
    },
  })
}

export function useDeleteProject() {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: (projectId: string) => projectsApi.delete(projectId),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: [PROJECTS_QUERY_KEY] })
    },
  })
}

export function useArchiveProject() {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: (projectId: string) => projectsApi.archive(projectId),
    onSuccess: (_, projectId) => {
      queryClient.invalidateQueries({ queryKey: [PROJECTS_QUERY_KEY, projectId] })
      queryClient.invalidateQueries({ queryKey: [PROJECTS_QUERY_KEY] })
    },
  })
}

export function useProjectStats(projectId: string) {
  return useQuery({
    queryKey: [PROJECTS_QUERY_KEY, projectId, 'stats'],
    queryFn: () => projectsApi.getStats(projectId),
    enabled: !!projectId,
  })
}

export function useProjectWebsites(projectId: string, page = 1, pageSize = 20) {
  return useQuery({
    queryKey: [PROJECTS_QUERY_KEY, projectId, 'websites', { page, pageSize }],
    queryFn: () => projectsApi.getWebsites(projectId, page, pageSize),
    enabled: !!projectId,
  })
}

export function useProjectVideos(projectId: string, page = 1, pageSize = 20) {
  return useQuery({
    queryKey: [PROJECTS_QUERY_KEY, projectId, 'videos', { page, pageSize }],
    queryFn: () => projectsApi.getVideos(projectId, page, pageSize),
    enabled: !!projectId,
  })
}