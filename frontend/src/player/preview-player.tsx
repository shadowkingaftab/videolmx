import { useState, useRef, useEffect } from 'react'
import { X, Play, Pause } from 'lucide-react'
import { Button } from '@/components/ui/button'

interface PreviewPlayerProps {
  video: any
  scenes: Array<{
    id: string
    title: string
    duration: number
    narration_text?: string
  }>
  onClose: () => void
}

export function PreviewPlayer({ video, scenes, onClose }: PreviewPlayerProps) {
  const [isPlaying, setIsPlaying] = useState(false)
  const [currentTime, setCurrentTime] = useState(0)
  const [currentScene, setCurrentScene] = useState(0)
  const intervalRef = useRef<NodeJS.Timeout>()

  const totalDuration = scenes.reduce((acc, scene) => acc + scene.duration, 0)
  const sortedScenes = [...scenes].sort((a, b) => a.order - b.order)

  useEffect(() => {
    if (isPlaying) {
      intervalRef.current = setInterval(() => {
        setCurrentTime((prev) => {
          const newTime = prev + 0.1
          if (newTime >= totalDuration) {
            setIsPlaying(false)
            clearInterval(intervalRef.current)
            return 0
          }

          // Update current scene
          let accumulated = 0
          for (let i = 0; i < sortedScenes.length; i++) {
            accumulated += sortedScenes[i].duration
            if (newTime < accumulated) {
              setCurrentScene(i)
              break
            }
          }

          return newTime
        })
      }, 100)
    } else {
      clearInterval(intervalRef.current)
    }

    return () => clearInterval(intervalRef.current)
  }, [isPlaying, totalDuration, sortedScenes])

  const handlePlayPause = () => {
    setIsPlaying(!isPlaying)
  }

  const handleClose = () => {
    setIsPlaying(false)
    clearInterval(intervalRef.current)
    onClose()
  }

  const progress = totalDuration > 0 ? (currentTime / totalDuration) * 100 : 0
  const currentSceneData = sortedScenes[currentScene]

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/80">
      <div className="w-full max-w-4xl rounded-lg bg-background p-6">
        <div className="mb-4 flex items-center justify-between">
          <h2 className="text-xl font-bold">Preview: {video.name}</h2>
          <Button variant="ghost" size="sm" onClick={handleClose}>
            <X className="h-4 w-4" />
          </Button>
        </div>

        {/* Preview container */}
        <div className="aspect-video overflow-hidden rounded-lg bg-black">
          <div className="flex h-full flex-col items-center justify-center p-8 text-center text-white">
            {/* Scene preview */}
            {currentSceneData && (
              <div className="space-y-4">
                <h3 className="text-2xl font-bold">{currentSceneData.title}</h3>
                {currentSceneData.narration_text && (
                  <p className="text-lg text-muted-foreground">
                    {currentSceneData.narration_text}
                  </p>
                )}
              </div>
            )}

            {/* Progress bar */}
            <div className="mt-8 w-full max-w-md">
              <div className="h-1 w-full bg-white/20">
                <div
                  className="h-full bg-primary transition-all duration-100"
                  style={{ width: `${progress}%` }}
                />
              </div>
              <div className="mt-2 flex justify-between text-sm text-muted-foreground">
                <span>{Math.floor(currentTime)}s</span>
                <span>{Math.floor(totalDuration)}s</span>
              </div>
            </div>

            {/* Controls */}
            <Button
              variant="outline"
              size="lg"
              className="mt-4"
              onClick={handlePlayPause}
            >
              {isPlaying ? (
                <Pause className="h-6 w-6" />
              ) : (
                <Play className="h-6 w-6" />
              )}
            </Button>
          </div>
        </div>

        {/* Scene list */}
        <div className="mt-4 max-h-32 overflow-auto">
          <div className="flex space-x-2">
            {sortedScenes.map((scene, index) => (
              <div
                key={scene.id}
                className={`flex-shrink-0 rounded border p-2 text-sm ${
                  index === currentScene
                    ? 'border-primary bg-primary/10'
                    : 'border-border'
                }`}
              >
                {scene.title}
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  )
}