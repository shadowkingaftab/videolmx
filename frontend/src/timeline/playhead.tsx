import { useRef, useEffect } from 'react'

interface PlayheadProps {
  currentTime: number
  totalDuration: number
  onTimeChange: (time: number) => void
}

export function Playhead({ currentTime, totalDuration, onTimeChange }: PlayheadProps) {
  const playheadRef = useRef<HTMLDivElement>(null)

  const percentage = totalDuration > 0 ? (currentTime / totalDuration) * 100 : 0

  useEffect(() => {
    if (playheadRef.current) {
      playheadRef.current.style.left = `${percentage}%`
    }
  }, [percentage])

  const handleMouseDown = (e: React.MouseEvent) => {
    const rect = e.currentTarget.getBoundingClientRect()
    const x = e.clientX - rect.left
    const percentage = Math.max(0, Math.min(1, x / rect.width))
    onTimeChange(percentage * totalDuration)

    const onMouseMove = (moveEvent: MouseEvent) => {
      const moveX = moveEvent.clientX - rect.left
      const movePercentage = Math.max(0, Math.min(1, moveX / rect.width))
      onTimeChange(movePercentage * totalDuration)
    }

    const onMouseUp = () => {
      document.removeEventListener('mousemove', onMouseMove)
      document.removeEventListener('mouseup', onMouseUp)
    }

    document.addEventListener('mousemove', onMouseMove)
    document.addEventListener('mouseup', onMouseUp)
  }

  return (
    <div
      ref={playheadRef}
      className="absolute top-0 z-10 h-full w-0.5 bg-primary"
      style={{ left: `${percentage}%` }}
    >
      <div
        className="absolute -left-2 -top-1 h-4 w-4 cursor-pointer rounded-full bg-primary"
        onMouseDown={handleMouseDown}
      >
        <div className="absolute left-1/2 top-1/2 h-2 w-2 -translate-x-1/2 -translate-y-1/2 rounded-full bg-white" />
      </div>
    </div>
  )
}