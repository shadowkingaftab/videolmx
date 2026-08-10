import { Slider } from '@/components/ui/slider'
import { formatTime } from '@/utils/format'

interface ScrubberProps {
  played: number
  duration: number
  onSeek: (played: number) => void
}

export function Scrubber({ played, duration, onSeek }: ScrubberProps) {
  const handleSeek = (value: number[]) => {
    onSeek(value[0])
  }

  return (
    <div className="flex items-center space-x-3">
      <span className="text-xs text-white/80">{formatTime(played * duration)}</span>
      <Slider
        value={[played]}
        onValueChange={handleSeek}
        max={1}
        step={0.001}
        className="flex-1"
      />
      <span className="text-xs text-white/80">{formatTime(duration)}</span>
    </div>
  )
}