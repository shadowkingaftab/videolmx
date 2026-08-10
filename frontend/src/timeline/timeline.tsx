import { useState, useRef } from 'react'
import { SceneTrack } from './scene-track'
import { AudioTrack } from './audio-track'
import { SubtitleTrack } from './subtitle-track'
import { Playhead } from './playhead'
import { ZoomControls } from './zoom-controls'
import { ScrollArea } from '@/components/ui/scroll-area'

interface TimelineProps {
  scenes: Array<{
    id: string
    order: number
    title: string
    duration: number
    thumbnail?: string
  }>
  onSceneUpdate: (scene: any) => void
}

export function Timeline({ scenes, onSceneUpdate }: TimelineProps) {
  const [zoom, setZoom] = useState(1)
  const [currentTime, setCurrentTime] = useState(0)
  const timelineRef = useRef<HTMLDivElement>(null)
  const totalDuration = scenes.reduce((acc, scene) => acc + scene.duration, 0)

  const sortedScenes = [...scenes].sort((a, b) => a.order - b.order)

  return (
    <div className="flex h-full flex-col bg-background">
      {/* Timeline header */}
      <div className="flex items-center justify-between border-b p-2">
        <div className="flex items-center space-x-4">
          <span className="text-sm font-medium">Timeline</span>
          <span className="text-sm text-muted-foreground">
            {scenes.length} scenes • {totalDuration.toFixed(1)}s
          </span>
        </div>
        <ZoomControls zoom={zoom} onZoomChange={setZoom} />
      </div>

      {/* Timeline tracks */}
      <div className="flex-1 overflow-hidden" ref={timelineRef}>
        <ScrollArea className="h-full">
          <div className="relative">
            {/* Playhead */}
            <Playhead
              currentTime={currentTime}
              totalDuration={totalDuration}
              onTimeChange={setCurrentTime}
            />

            {/* Tracks */}
            <div className="space-y-1 p-2">
              <SceneTrack
                scenes={sortedScenes}
                zoom={zoom}
                onSceneUpdate={onSceneUpdate}
              />
              <AudioTrack scenes={sortedScenes} zoom={zoom} />
              <SubtitleTrack scenes={sortedScenes} zoom={zoom} />
            </div>

            {/* Timeline ruler */}
            <div className="mt-2 h-6 border-t">
              <div className="flex h-full items-center">
                {Array.from({ length: Math.ceil(totalDuration) + 1 }).map((_, i) => (
                  <div
                    key={i}
                    className="relative flex h-full items-start"
                    style={{ width: `${60 * zoom}px` }}
                  >
                    <span className="text-xs text-muted-foreground">{i}s</span>
                    <div className="absolute left-0 top-0 h-2 w-px bg-border" />
                  </div>
                ))}
              </div>
            </div>
          </div>
        </ScrollArea>
      </div>
    </div>
  )
}