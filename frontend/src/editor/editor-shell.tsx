import { ReactNode } from 'react'

interface EditorShellProps {
  children: ReactNode
}

export function EditorShell({ children }: EditorShellProps) {
  return (
    <div className="flex h-full flex-col bg-background">
      <div className="flex-1 overflow-hidden">{children}</div>
    </div>
  )
}