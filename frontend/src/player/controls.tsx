import { Play, Pause, Volume2, VolumeX } from 'lucide-react'
import { Button } from '@/components/ui/button'
import { Slider } from '@/components/ui/slider'

interface ControlsProps {
  playing: boolean
  onPlayPause: () => void
  volume: number
  onVolumeChange: (volume: number) => void
}

export function Controls({
  playing,
  onPlayPause,
  volume,
  onVolumeChange,
}: ControlsProps) {
  const handleVolumeToggle = () => {
    if (volume > 0) {
      onVolumeChange(0)
    } else {
      onVolumeChange(0.8)
    }
  }

  return (
    <div className="flex items-center space-x-4">
      <Button
        size="sm"
        variant="ghost"
        className="text-white hover:bg-white/20"
        onClick={onPlayPause}
      >
        {playing ? (
          <Pause className="h-5 w-5" />
        ) : (
          <Play className="h-5 w-5" />
        )}
      </Button>

      <div className="flex items-center space-x-2">
        <Button
          size="sm"
          variant="ghost"
          className="text-white hover:bg-white/20"
          onClick={handleVolumeToggle}
        >
          {volume > 0 ? (
            <Volume2 className="h-4 w-4" />
          ) : (
            <VolumeX className="h-4 w-4" />
          )}
        </Button>
        <Slider
          value={[volume]}
          onValueChange={([value]) => onVolumeChange(value)}
          max={1}
          step={0.01}
          className="w-20"
        />
      </div>
    </div>
  )
}