import { createContext, useContext, ReactNode } from 'react'
import { useEditorStore } from '@/store/editor-store'

const EditorContext = createContext<ReturnType<typeof useEditorStore> | null>(null)

export function EditorProvider({ children }: { children: ReactNode }) {
  const store = useEditorStore()
  return <EditorContext.Provider value={store}>{children}</EditorContext.Provider>
}

export function useEditor() {
  const context = useContext(EditorContext)
  if (!context) {
    throw new Error('useEditor must be used within an EditorProvider')
  }
  return context
}