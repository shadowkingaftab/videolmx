import { ZoomIn, ZoomOut } from 'lucide-react'
import { Button } from '@/components/ui/button'

interface ZoomControlsProps {
  zoom: number
  onZoomChange: (zoom: number) => void
}

export function ZoomControls({ zoom, onZoomChange }: ZoomControlsProps) {
  const handleZoomIn = () => {
    onZoomChange(Math.min(zoom + 0.25, 3))
  }

  const handleZoomOut = () => {
    onZoomChange(Math.max(zoom - 0.25, 0.25))
  }

  return (
    <div className="flex items-center space-x-2">
      <span className="text-sm text-muted-foreground">
        {Math.round(zoom * 100)}%
      </span>
      <Button size="sm" variant="ghost" onClick={handleZoomOut}>
        <ZoomOut className="h-4 w-4" />
      </Button>
      <Button size="sm" variant="ghost" onClick={handleZoomIn}>
        <ZoomIn className="h-4 w-4" />
      </Button>
    </div>
  )
}