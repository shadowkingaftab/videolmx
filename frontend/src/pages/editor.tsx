import { useState, useEffect } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import { EditorShell } from '@/editor/editor-shell'
import { ScriptEditor } from '@/editor/script-editor'
import { StoryboardEditor } from '@/editor/storyboard-editor'
import { SceneEditor } from '@/editor/scene-editor'
import { Timeline } from '@/timeline/timeline'
import { PreviewPlayer } from '@/player/preview-player'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'
import { Button } from '@/components/ui/button'
import { ArrowLeft, Save, Play, Settings } from 'lucide-react'
import { useVideo, useUpdateVideo } from '@/hooks/use-video'
import { useEditorStore } from '@/store/editor-store'
import { toast } from 'react-hot-toast'

export function EditorPage() {
  const { videoId } = useParams<{ videoId: string }>()
  const navigate = useNavigate()
  const [activeTab, setActiveTab] = useState('storyboard')
  const [isPreviewOpen, setIsPreviewOpen] = useState(false)

  const { data: video, isLoading } = useVideo(videoId!)
  const updateVideo = useUpdateVideo()
  const { scenes, setScenes, setActiveScene } = useEditorStore()

  useEffect(() => {
    if (video?.storyboard?.scenes) {
      setScenes(video.storyboard.scenes)
    }
  }, [video])

  const handleSave = async () => {
    try {
      await updateVideo.mutateAsync({
        videoId: videoId!,
        data: { storyboard: { scenes } },
      })
      toast.success('Video saved')
    } catch (err) {
      toast.error('Failed to save video')
    }
  }

  if (isLoading) {
    return (
      <div className="flex h-screen items-center justify-center">
        <div className="h-8 w-8 animate-spin rounded-full border-4 border-primary border-t-transparent" />
      </div>
    )
  }

  if (!video) {
    return <div>Video not found</div>
  }

  return (
    <div className="flex h-screen flex-col bg-background">
      {/* Header */}
      <header className="flex h-14 items-center justify-between border-b px-4">
        <div className="flex items-center space-x-4">
          <Button asChild variant="ghost" size="sm">
            <Link to={`/videos/${videoId}`}>
              <ArrowLeft className="h-4 w-4" />
            </Link>
          </Button>
          <h1 className="text-lg font-semibold">{video.name}</h1>
          <span className="text-sm text-muted-foreground">
            {video.status}
          </span>
        </div>
        <div className="flex items-center space-x-2">
          <Button
            variant="outline"
            size="sm"
            onClick={() => setIsPreviewOpen(true)}
          >
            <Play className="mr-2 h-4 w-4" />
            Preview
          </Button>
          <Button size="sm" onClick={handleSave} disabled={updateVideo.isPending}>
            <Save className="mr-2 h-4 w-4" />
            {updateVideo.isPending ? 'Saving...' : 'Save'}
          </Button>
        </div>
      </header>

      {/* Editor Content */}
      <div className="flex-1 overflow-hidden">
        <EditorShell>
          <Tabs value={activeTab} onValueChange={setActiveTab} className="h-full">
            <TabsList className="border-b">
              <TabsTrigger value="storyboard">Storyboard</TabsTrigger>
              <TabsTrigger value="script">Script</TabsTrigger>
              <TabsTrigger value="scenes">Scenes</TabsTrigger>
              <TabsTrigger value="timeline">Timeline</TabsTrigger>
            </TabsList>

            <TabsContent value="storyboard" className="h-[calc(100%-48px)] overflow-auto">
              <StoryboardEditor
                scenes={scenes}
                onSceneSelect={(scene) => setActiveScene(scene)}
                onSceneUpdate={(scene) => {
                  const index = scenes.findIndex((s) => s.id === scene.id)
                  if (index >= 0) {
                    const updated = [...scenes]
                    updated[index] = scene
                    setScenes(updated)
                  }
                }}
              />
            </TabsContent>

            <TabsContent value="script" className="h-[calc(100%-48px)] overflow-auto">
              <ScriptEditor
                script={video.script}
                onUpdate={(content) => {
                  // Update script content
                }}
              />
            </TabsContent>

            <TabsContent value="scenes" className="h-[calc(100%-48px)] overflow-auto">
              <SceneEditor
                scenes={scenes}
                onSceneUpdate={(scene) => {
                  const index = scenes.findIndex((s) => s.id === scene.id)
                  if (index >= 0) {
                    const updated = [...scenes]
                    updated[index] = scene
                    setScenes(updated)
                  }
                }}
                onSceneAdd={() => {
                  // Add new scene
                }}
                onSceneDelete={(sceneId) => {
                  setScenes(scenes.filter((s) => s.id !== sceneId))
                }}
              />
            </TabsContent>

            <TabsContent value="timeline" className="h-[calc(100%-48px)]">
              <Timeline
                scenes={scenes}
                onSceneUpdate={(scene) => {
                  const index = scenes.findIndex((s) => s.id === scene.id)
                  if (index >= 0) {
                    const updated = [...scenes]
                    updated[index] = scene
                    setScenes(updated)
                  }
                }}
              />
            </TabsContent>
          </Tabs>
        </EditorShell>
      </div>

      {/* Preview Player Modal */}
      {isPreviewOpen && (
        <PreviewPlayer
          video={video}
          scenes={scenes}
          onClose={() => setIsPreviewOpen(false)}
        />
      )}
    </div>
  )
}