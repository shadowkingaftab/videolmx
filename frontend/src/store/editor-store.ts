import { create } from 'zustand'

export interface Scene {
  id: string
  order: number
  title: string
  description?: string
  scene_type: string
  duration: number
  narration_text?: string
  thumbnail?: string
}

interface EditorState {
  scenes: Scene[]
  activeSceneId: string | null
  isPlaying: boolean
  currentTime: number
  zoom: number
  setScenes: (scenes: Scene[]) => void
  setActiveScene: (scene: Scene | null) => void
  updateScene: (scene: Scene) => void
  addScene: (scene: Scene) => void
  removeScene: (sceneId: string) => void
  reorderScenes: (startIndex: number, endIndex: number) => void
  setIsPlaying: (isPlaying: boolean) => void
  setCurrentTime: (time: number) => void
  setZoom: (zoom: number) => void
}

export const useEditorStore = create<EditorState>((set, get) => ({
  scenes: [],
  activeSceneId: null,
  isPlaying: false,
  currentTime: 0,
  zoom: 1,
  setScenes: (scenes) => set({ scenes }),
  setActiveScene: (scene) => set({ activeSceneId: scene?.id || null }),
  updateScene: (scene) => {
    const { scenes } = get()
    const index = scenes.findIndex((s) => s.id === scene.id)
    if (index >= 0) {
      const updated = [...scenes]
      updated[index] = scene
      set({ scenes: updated })
    }
  },
  addScene: (scene) => {
    const { scenes } = get()
    set({ scenes: [...scenes, scene] })
  },
  removeScene: (sceneId) => {
    const { scenes } = get()
    set({ scenes: scenes.filter((s) => s.id !== sceneId) })
  },
  reorderScenes: (startIndex, endIndex) => {
    const { scenes } = get()
    const items = Array.from(scenes)
    const [reorderedItem] = items.splice(startIndex, 1)
    items.splice(endIndex, 0, reorderedItem)
    // Update order property
    const reordered = items.map((item, index) => ({
      ...item,
      order: index,
    }))
    set({ scenes: reordered })
  },
  setIsPlaying: (isPlaying) => set({ isPlaying }),
  setCurrentTime: (currentTime) => set({ currentTime }),
  setZoom: (zoom) => set({ zoom }),
}))