interface AudioTrackProps {
  scenes: Array<{
    id: string
    duration: number
    narration_text?: string
  }>
  zoom: number
}

export function AudioTrack({ scenes, zoom }: AudioTrackProps) {
  return (
    <div className="space-y-1">
      <div className="flex items-center">
        <div className="w-24 flex-shrink-0 text-sm font-medium">Audio</div>
        <div className="relative h-8 flex-1 rounded bg-secondary/30">
          {scenes.map((scene, index) => (
            <div
              key={scene.id}
              className="absolute top-0 h-full rounded bg-primary/20"
              style={{
                left: scenes
                  .slice(0, index)
                  .reduce((acc, s) => acc + s.duration * 60 * zoom, 0),
                width: scene.duration * 60 * zoom,
              }}
            >
              <div className="flex h-full items-center justify-center text-xs text-muted-foreground">
                {scene.narration_text ? '🎤' : '🔇'}
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  )
}