import { create } from 'zustand'

interface ProjectState {
  selectedProjectId: string | null
  selectedWebsiteId: string | null
  selectedVideoId: string | null
  setSelectedProject: (id: string | null) => void
  setSelectedWebsite: (id: string | null) => void
  setSelectedVideo: (id: string | null) => void
}

export const useProjectStore = create<ProjectState>((set) => ({
  selectedProjectId: null,
  selectedWebsiteId: null,
  selectedVideoId: null,
  setSelectedProject: (id) => set({ selectedProjectId: id }),
  setSelectedWebsite: (id) => set({ selectedWebsiteId: id }),
  setSelectedVideo: (id) => set({ selectedVideoId: id }),
}))