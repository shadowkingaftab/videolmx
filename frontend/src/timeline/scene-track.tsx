import { useRef, useState } from 'react'
import { GripVertical } from 'lucide-react'
import { cn } from '@/utils/cn'

interface SceneTrackProps {
  scenes: Array<{
    id: string
    order: number
    title: string
    duration: number
    thumbnail?: string
  }>
  zoom: number
  onSceneUpdate: (scene: any) => void
}

export function SceneTrack({ scenes, onSceneUpdate, zoom }: SceneTrackProps) {
  const [dragging, setDragging] = useState<string | null>(null)
  const trackRef = useRef<HTMLDivElement>(null)

  const getSceneWidth = (duration: number) => duration * 60 * zoom

  const handleMouseDown = (e: React.MouseEvent, sceneId: string) => {
    setDragging(sceneId)
    const startX = e.clientX
    const scene = scenes.find((s) => s.id === sceneId)
    if (!scene) return

    const onMouseMove = (moveEvent: MouseEvent) => {
      const deltaX = (moveEvent.clientX - startX) / (60 * zoom)
      const newDuration = Math.max(1, scene.duration + deltaX)
      onSceneUpdate({ ...scene, duration: newDuration })
    }

    const onMouseUp = () => {
      setDragging(null)
      document.removeEventListener('mousemove', onMouseMove)
      document.removeEventListener('mouseup', onMouseUp)
    }

    document.addEventListener('mousemove', onMouseMove)
    document.addEventListener('mouseup', onMouseUp)
  }

  return (
    <div className="space-y-1">
      <div className="flex items-center">
        <div className="w-24 flex-shrink-0 text-sm font-medium">Scenes</div>
        <div
          ref={trackRef}
          className="relative h-16 flex-1 rounded bg-secondary/50"
        >
          {scenes.map((scene, index) => (
            <div
              key={scene.id}
              className={cn(
                'absolute top-0 h-full rounded border-2 border-primary/20 bg-card p-1 transition-opacity',
                dragging === scene.id && 'opacity-50'
              )}
              style={{
                left: scenes
                  .slice(0, index)
                  .reduce((acc, s) => acc + getSceneWidth(s.duration), 0),
                width: getSceneWidth(scene.duration),
              }}
            >
              <div className="flex h-full items-center justify-between">
                <span className="truncate text-xs">{scene.title}</span>
                <div
                  className="cursor-ew-resize p-1 hover:bg-primary/20"
                  onMouseDown={(e) => handleMouseDown(e, scene.id)}
                >
                  <GripVertical className="h-3 w-3 text-muted-foreground" />
                </div>
              </div>
              {scene.thumbnail && (
                <img
                  src={scene.thumbnail}
                  alt={scene.title}
                  className="absolute inset-0 h-full w-full rounded object-cover opacity-30"
                />
              )}
            </div>
          ))}
        </div>
      </div>
    </div>
  )
}