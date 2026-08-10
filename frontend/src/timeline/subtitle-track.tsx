interface SubtitleTrackProps {
  scenes: Array<{
    id: string
    duration: number
    title: string
  }>
  zoom: number
}

export function SubtitleTrack({ scenes, zoom }: SubtitleTrackProps) {
  return (
    <div className="space-y-1">
      <div className="flex items-center">
        <div className="w-24 flex-shrink-0 text-sm font-medium">Subtitles</div>
        <div className="relative h-8 flex-1 rounded bg-secondary/20">
          {scenes.map((scene, index) => (
            <div
              key={scene.id}
              className="absolute top-1/2 h-4 -translate-y-1/2 rounded bg-primary/10 px-2 text-xs"
              style={{
                left: scenes
                  .slice(0, index)
                  .reduce((acc, s) => acc + s.duration * 60 * zoom, 0) + 4,
                width: scene.duration * 60 * zoom - 8,
              }}
            >
              <span className="truncate">{scene.title}</span>
            </div>
          ))}
        </div>
      </div>
    </div>
  )
}