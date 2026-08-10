import { Maximize, Minimize } from 'lucide-react'
import { Button } from '@/components/ui/button'
import { useState } from 'react'

interface FullscreenButtonProps {
  onClick: () => void
}

export function FullscreenButton({ onClick }: FullscreenButtonProps) {
  const [isFullscreen, setIsFullscreen] = useState(false)

  const handleClick = () => {
    setIsFullscreen(!isFullscreen)
    onClick()
  }

  return (
    <Button
      size="sm"
      variant="ghost"
      className="text-white hover:bg-white/20"
      onClick={handleClick}
    >
      {isFullscreen ? (
        <Minimize className="h-5 w-5" />
      ) : (
        <Maximize className="h-5 w-5" />
      )}
    </Button>
  )
}