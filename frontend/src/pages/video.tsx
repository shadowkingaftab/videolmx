import { useState } from 'react'
import { useParams, Link, useNavigate } from 'react-router-dom'
import { ArrowLeft, Play, Download, Edit, Trash2, Share2 } from 'lucide-react'
import { useVideo, useRenderVideo, useDeleteVideo } from '@/hooks/use-video'
import { useExports } from '@/hooks/use-video'
import { Button } from '@/components/ui/button'
import { VideoPlayer } from '@/player/video-player'
import { StatusBadge } from '@/components/status-badge'
import { ProgressBar } from '@/components/progress-bar'
import { ConfirmDialog } from '@/components/confirm-dialog'
import { toast } from 'react-hot-toast'

export function VideoPage() {
  const { videoId } = useParams<{ videoId: string }>()
  const navigate = useNavigate()
  const [showDeleteDialog, setShowDeleteDialog] = useState(false)

  const { data: video, isLoading } = useVideo(videoId!)
  const { data: exports } = useExports(videoId!)
  const renderVideo = useRenderVideo()
  const deleteVideo = useDeleteVideo()

  const handleRender = async () => {
    try {
      await renderVideo.mutateAsync({
        videoId: videoId!,
        resolution: '1920x1080',
        fps: 30,
        quality: 'medium',
      })
      toast.success('Video rendering started')
    } catch (err) {
      toast.error('Failed to start rendering')
    }
  }

  const handleDelete = async () => {
    try {
      await deleteVideo.mutateAsync(videoId!)
      toast.success('Video deleted')
      navigate('/dashboard')
    } catch (err) {
      toast.error('Failed to delete video')
    }
  }

  if (isLoading) {
    return (
      <div className="flex h-96 items-center justify-center">
        <div className="h-8 w-8 animate-spin rounded-full border-4 border-primary border-t-transparent" />
      </div>
    )
  }

  if (!video) {
    return <div>Video not found</div>
  }

  const isReady = video.status === 'ready'
  const isRendering = video.status === 'rendering'

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div className="flex items-center space-x-4">
          <Button asChild variant="ghost" size="sm">
            <Link to="/dashboard">
              <ArrowLeft className="h-4 w-4" />
            </Link>
          </Button>
          <div>
            <h1 className="text-3xl font-bold">{video.name}</h1>
            <div className="flex items-center space-x-2">
              <StatusBadge status={video.status} />
              <span className="text-sm text-muted-foreground">
                {video.duration ? `${Math.round(video.duration)}s` : 'No duration'}
              </span>
            </div>
          </div>
        </div>
        <div className="flex space-x-2">
          <Button asChild variant="outline">
            <Link to={`/editor/${videoId}`}>
              <Edit className="mr-2 h-4 w-4" />
              Edit
            </Link>
          </Button>
          <Button onClick={handleRender} disabled={isRendering}>
            <Play className="mr-2 h-4 w-4" />
            {isRendering ? 'Rendering...' : 'Render'}
          </Button>
          <Button variant="destructive" onClick={() => setShowDeleteDialog(true)}>
            <Trash2 className="h-4 w-4" />
          </Button>
        </div>
      </div>

      {/* Video Player */}
      <div className="aspect-video overflow-hidden rounded-lg bg-black">
        {isReady && video.file_url ? (
          <VideoPlayer src={video.file_url} />
        ) : (
          <div className="flex h-full items-center justify-center">
            <div className="text-center text-white">
              {isRendering ? (
                <>
                  <div className="mb-4 h-12 w-12 animate-spin rounded-full border-4 border-white border-t-transparent" />
                  <p>Rendering video...</p>
                  <ProgressBar value={video.progress || 0} className="mt-4 w-64" />
                </>
              ) : (
                <>
                  <Play className="mx-auto mb-4 h-12 w-12 opacity-50" />
                  <p className="text-muted-foreground">
                    {video.status === 'draft'
                      ? 'Video not rendered yet'
                      : 'Video not available'}
                  </p>
                  <Button
                    variant="outline"
                    className="mt-4"
                    onClick={handleRender}
                  >
                    Render Video
                  </Button>
                </>
              )}
            </div>
          </div>
        )}
      </div>

      {/* Actions */}
      <div className="grid gap-4 md:grid-cols-4">
        <Button asChild variant="outline" className="h-24 flex-col space-y-2">
          <Link to={`/editor/${videoId}`}>
            <Edit className="h-6 w-6" />
            <span>Edit</span>
          </Link>
        </Button>
        <Button
          variant="outline"
          className="h-24 flex-col space-y-2"
          onClick={handleRender}
          disabled={isRendering}
        >
          <Play className="h-6 w-6" />
          <span>Render</span>
        </Button>
        <Button
          variant="outline"
          className="h-24 flex-col space-y-2"
          disabled={!isReady}
        >
          <Download className="h-6 w-6" />
          <span>Download</span>
        </Button>
        <Button
          variant="outline"
          className="h-24 flex-col space-y-2"
          disabled={!isReady}
        >
          <Share2 className="h-6 w-6" />
          <span>Share</span>
        </Button>
      </div>

      {/* Exports */}
      {exports && exports.length > 0 && (
        <div className="rounded-lg border bg-card p-4">
          <h3 className="mb-2 text-sm font-medium text-muted-foreground">Exports</h3>
          <div className="space-y-2">
            {exports.map((exp) => (
              <div
                key={exp.id}
                className="flex items-center justify-between rounded border p-2"
              >
                <div>
                  <span className="font-medium">{exp.format}</span>
                  <span className="ml-2 text-sm text-muted-foreground">
                    {exp.quality}
                  </span>
                </div>
                <StatusBadge status={exp.status} />
                {exp.file_url && (
                  <Button asChild size="sm" variant="ghost">
                    <a href={exp.file_url} download>
                      <Download className="h-4 w-4" />
                    </a>
                  </Button>
                )}
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Delete Confirmation */}
      <ConfirmDialog
        open={showDeleteDialog}
        onOpenChange={setShowDeleteDialog}
        title="Delete Video"
        description="Are you sure you want to delete this video? This action cannot be undone."
        confirmLabel="Delete"
        onConfirm={handleDelete}
        variant="destructive"
      />
    </div>
  )
}