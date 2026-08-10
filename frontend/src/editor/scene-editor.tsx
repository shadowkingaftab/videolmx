import { useState } from 'react'
import { Plus, Trash2, MoveUp, MoveDown } from 'lucide-react'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Select } from '@/components/ui/select'
import { Textarea } from '@/components/ui/textarea'

interface SceneEditorProps {
  scenes: Array<{
    id: string
    order: number
    title: string
    description?: string
    scene_type: string
    duration: number
    narration_text?: string
  }>
  onSceneUpdate: (scene: any) => void
  onSceneAdd: () => void
  onSceneDelete: (sceneId: string) => void
}

export function SceneEditor({
  scenes,
  onSceneUpdate,
  onSceneAdd,
  onSceneDelete,
}: SceneEditorProps) {
  const [editingId, setEditingId] = useState<string | null>(null)

  const sceneTypes = [
    'intro',
    'feature',
    'benefit',
    'testimonial',
    'pricing',
    'comparison',
    'conclusion',
    'call-to-action',
  ]

  const sortedScenes = [...scenes].sort((a, b) => a.order - b.order)

  const moveScene = (index: number, direction: number) => {
    const newIndex = index + direction
    if (newIndex < 0 || newIndex >= sortedScenes.length) return

    const item = sortedScenes[index]
    const other = sortedScenes[newIndex]

    onSceneUpdate({ ...item, order: newIndex })
    onSceneUpdate({ ...other, order: index })
  }

  return (
    <div className="space-y-4 p-4">
      <div className="flex items-center justify-between">
        <h2 className="text-lg font-semibold">Scene Editor</h2>
        <Button size="sm" onClick={onSceneAdd}>
          <Plus className="mr-2 h-4 w-4" />
          Add Scene
        </Button>
      </div>

      <div className="space-y-4">
        {sortedScenes.map((scene, index) => (
          <div
            key={scene.id}
            className="rounded-lg border bg-card p-4 transition-colors hover:border-primary/50"
          >
            <div className="flex items-start justify-between">
              <div className="flex-1 space-y-3">
                <div className="flex items-center space-x-2">
                  <span className="text-sm font-medium text-muted-foreground">
                    #{index + 1}
                  </span>
                  {editingId === scene.id ? (
                    <Input
                      value={scene.title}
                      onChange={(e) =>
                        onSceneUpdate({ ...scene, title: e.target.value })
                      }
                      className="flex-1"
                      autoFocus
                    />
                  ) : (
                    <h3
                      className="flex-1 cursor-pointer text-lg font-medium hover:text-primary"
                      onClick={() => setEditingId(scene.id)}
                    >
                      {scene.title}
                    </h3>
                  )}
                </div>

                <div className="grid gap-3 md:grid-cols-2">
                  <div>
                    <label className="text-sm text-muted-foreground">Type</label>
                    <Select
                      value={scene.scene_type}
                      onValueChange={(value) =>
                        onSceneUpdate({ ...scene, scene_type: value })
                      }
                    >
                      {sceneTypes.map((type) => (
                        <option key={type} value={type}>
                          {type.replace('-', ' ').toUpperCase()}
                        </option>
                      ))}
                    </Select>
                  </div>

                  <div>
                    <label className="text-sm text-muted-foreground">
                      Duration (seconds)
                    </label>
                    <Input
                      type="number"
                      value={scene.duration}
                      onChange={(e) =>
                        onSceneUpdate({
                          ...scene,
                          duration: parseFloat(e.target.value) || 0,
                        })
                      }
                      min={1}
                      max={30}
                    />
                  </div>
                </div>

                <div>
                  <label className="text-sm text-muted-foreground">
                    Description
                  </label>
                  <Textarea
                    value={scene.description || ''}
                    onChange={(e) =>
                      onSceneUpdate({ ...scene, description: e.target.value })
                    }
                    rows={2}
                  />
                </div>

                {scene.narration_text && (
                  <div>
                    <label className="text-sm text-muted-foreground">
                      Narration
                    </label>
                    <div className="rounded bg-secondary p-2 text-sm">
                      {scene.narration_text}
                    </div>
                  </div>
                )}
              </div>

              <div className="ml-4 flex flex-col space-y-1">
                <Button
                  size="sm"
                  variant="ghost"
                  onClick={() => moveScene(index, -1)}
                  disabled={index === 0}
                >
                  <MoveUp className="h-4 w-4" />
                </Button>
                <Button
                  size="sm"
                  variant="ghost"
                  onClick={() => moveScene(index, 1)}
                  disabled={index === sortedScenes.length - 1}
                >
                  <MoveDown className="h-4 w-4" />
                </Button>
                <Button
                  size="sm"
                  variant="destructive"
                  onClick={() => onSceneDelete(scene.id)}
                >
                  <Trash2 className="h-4 w-4" />
                </Button>
              </div>
            </div>
          </div>
        ))}
      </div>

      {scenes.length === 0 && (
        <div className="flex h-64 items-center justify-center rounded-lg border-2 border-dashed">
          <div className="text-center">
            <p className="text-muted-foreground">No scenes yet</p>
            <p className="text-sm text-muted-foreground">
              Add scenes to build your video storyboard
            </p>
          </div>
        </div>
      )}
    </div>
  )
}