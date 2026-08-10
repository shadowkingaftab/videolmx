import { useRef, useState, useEffect } from 'react'
import ReactPlayer from 'react-player'
import { Controls } from './controls'
import { Scrubber } from './scrubber'
import { FullscreenButton } from './fullscreen-button'

interface VideoPlayerProps {
  src: string
  autoPlay?: boolean
  onProgress?: (state: { played: number; playedSeconds: number }) => void
  onEnded?: () => void
}

export function VideoPlayer({
  src,
  autoPlay = false,
  onProgress,
  onEnded,
}: VideoPlayerProps) {
  const [playing, setPlaying] = useState(autoPlay)
  const [volume, setVolume] = useState(0.8)
  const [played, setPlayed] = useState(0)
  const [duration, setDuration] = useState(0)
  const [isReady, setIsReady] = useState(false)
  const playerRef = useRef<ReactPlayer>(null)
  const containerRef = useRef<HTMLDivElement>(null)

  const handlePlayPause = () => {
    setPlaying(!playing)
  }

  const handleVolumeChange = (newVolume: number) => {
    setVolume(newVolume)
  }

  const handleSeek = (newPlayed: number) => {
    setPlayed(newPlayed)
    if (playerRef.current) {
      playerRef.current.seekTo(newPlayed)
    }
  }

  const handleProgress = (state: { played: number; playedSeconds: number }) => {
    setPlayed(state.played)
    onProgress?.(state)
  }

  const handleDuration = (duration: number) => {
    setDuration(duration)
  }

  const handleReady = () => {
    setIsReady(true)
  }

  const handleFullscreen = () => {
    if (containerRef.current) {
      if (document.fullscreenElement) {
        document.exitFullscreen()
      } else {
        containerRef.current.requestFullscreen()
      }
    }
  }

  return (
    <div ref={containerRef} className="relative aspect-video bg-black">
      <ReactPlayer
        ref={playerRef}
        url={src}
        playing={playing}
        volume={volume}
        width="100%"
        height="100%"
        onProgress={handleProgress}
        onDuration={handleDuration}
        onReady={handleReady}
        onEnded={onEnded}
        config={{
          file: {
            attributes: {
              controlsList: 'nodownload',
            },
          },
        }}
      />

      {isReady && (
        <div className="absolute bottom-0 left-0 right-0 bg-gradient-to-t from-black/80 to-transparent p-4">
          <Scrubber
            played={played}
            duration={duration}
            onSeek={handleSeek}
          />
          <div className="flex items-center justify-between">
            <Controls
              playing={playing}
              onPlayPause={handlePlayPause}
              volume={volume}
              onVolumeChange={handleVolumeChange}
            />
            <FullscreenButton onClick={handleFullscreen} />
          </div>
        </div>
      )}
    </div>
  )
}