import { useState } from 'react'
import { Clock, Play, Pause } from 'lucide-react'
import { Button } from '@/components/ui/button'
import { Slider } from '@/components/ui/slider'
import { Input } from '@/components/ui/input'
import { formatTime } from '@/utils/format'

interface TimingEditorProps {
  scenes: Array<{
    id: string
    duration: number
    title: string
  }>
  onDurationChange: (sceneId: string, duration: number) => void
  totalDuration: number
}

export function TimingEditor({
  scenes,
  onDurationChange,
  totalDuration,
}: TimingEditorProps) {
  const [isPlaying, setIsPlaying] = useState(false)
  const [currentTime, setCurrentTime] = useState(0)

  const handlePlayPause = () => {
    setIsPlaying(!isPlaying)
  }

  const handleTimeChange = (value: number[]) => {
    setCurrentTime(value[0])
  }

  const getCurrentScene = () => {
    let accumulated = 0
    for (const scene of scenes) {
      accumulated += scene.duration
      if (currentTime < accumulated) {
        return scene
      }
    }
    return scenes[scenes.length - 1]
  }

  const currentScene = getCurrentScene()

  return (
    <div className="space-y-4 p-4">
      <div className="flex items-center justify-between">
        <h2 className="text-lg font-semibold">Timing</h2>
        <div className="flex items-center space-x-2">
          <span className="text-sm text-muted-foreground">
            {formatTime(currentTime)} / {formatTime(totalDuration)}
          </span>
          <Button size="sm" variant="outline" onClick={handlePlayPause}>
            {isPlaying ? (
              <Pause className="h-4 w-4" />
            ) : (
              <Play className="h-4 w-4" />
            )}
          </Button>
        </div>
      </div>

      <div className="space-y-4">
        {/* Timeline slider */}
        <Slider
          value={[currentTime]}
          onValueChange={handleTimeChange}
          max={totalDuration}
          step={0.1}
          className="w-full"
        />

        {/* Scene timing controls */}
        <div className="rounded-lg border bg-card p-4">
          <div className="flex items-center justify-between">
            <div>
              <p className="font-medium">{currentScene?.title || 'No scene'}</p>
              <p className="text-sm text-muted-foreground">
                Current scene
              </p>
            </div>
            <div className="flex items-center space-x-2">
              <Clock className="h-4 w-4 text-muted-foreground" />
              <Input
                type="number"
                value={currentScene?.duration || 0}
                onChange={(e) => {
                  if (currentScene) {
                    const value = parseFloat(e.target.value)
                    if (!isNaN(value) && value > 0) {
                      onDurationChange(currentScene.id, value)
                    }
                  }
                }}
                className="w-20"
                min={1}
                step={0.5}
              />
              <span className="text-sm text-muted-foreground">s</span>
            </div>
          </div>
        </div>

        {/* Scene list with durations */}
        <div className="space-y-1">
          <p className="text-sm font-medium text-muted-foreground">All Scenes</p>
          {scenes.map((scene) => (
            <div
              key={scene.id}
              className={`flex items-center justify-between rounded px-3 py-2 text-sm ${
                scene.id === currentScene?.id
                  ? 'bg-primary/10'
                  : 'hover:bg-secondary/50'
              }`}
            >
              <span>{scene.title}</span>
              <div className="flex items-center space-x-2">
                <span className="text-muted-foreground">
                  {scene.duration.toFixed(1)}s
                </span>
                <Button
                  size="sm"
                  variant="ghost"
                  className="h-6 w-6 p-0"
                  onClick={() => {
                    // Jump to this scene
                    let accumulated = 0
                    for (const s of scenes) {
                      if (s.id === scene.id) break
                      accumulated += s.duration
                    }
                    setCurrentTime(accumulated)
                  }}
                >
                  <Play className="h-3 w-3" />
                </Button>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  )
}