import { DragDropContext, Droppable, Draggable } from '@hello-pangea/dnd'
import { GripVertical, Plus, Trash2 } from 'lucide-react'
import { Button } from '@/components/ui/button'
import { SceneCard } from '@/components/scene-card'

interface StoryboardEditorProps {
  scenes: Array<{
    id: string
    order: number
    title: string
    description?: string
    scene_type: string
    duration: number
    thumbnail?: string
  }>
  onSceneSelect: (scene: any) => void
  onSceneUpdate: (scene: any) => void
}

export function StoryboardEditor({
  scenes,
  onSceneSelect,
  onSceneUpdate,
}: StoryboardEditorProps) {
  const handleDragEnd = (result: any) => {
    if (!result.destination) return

    const items = Array.from(scenes)
    const [reorderedItem] = items.splice(result.source.index, 1)
    items.splice(result.destination.index, 0, reorderedItem)

    // Update order
    items.forEach((item, index) => {
      onSceneUpdate({ ...item, order: index })
    })
  }

  return (
    <div className="p-4">
      <div className="mb-4 flex items-center justify-between">
        <h2 className="text-lg font-semibold">Storyboard</h2>
        <Button size="sm">
          <Plus className="mr-2 h-4 w-4" />
          Add Scene
        </Button>
      </div>

      <DragDropContext onDragEnd={handleDragEnd}>
        <Droppable droppableId="scenes">
          {(provided) => (
            <div {...provided.droppableProps} ref={provided.innerRef} className="space-y-2">
              {scenes
                .sort((a, b) => a.order - b.order)
                .map((scene, index) => (
                  <Draggable key={scene.id} draggableId={scene.id} index={index}>
                    {(provided) => (
                      <div
                        ref={provided.innerRef}
                        {...provided.draggableProps}
                        className="flex items-center gap-2"
                      >
                        <div {...provided.dragHandleProps} className="cursor-grab">
                          <GripVertical className="h-5 w-5 text-muted-foreground" />
                        </div>
                        <SceneCard
                          scene={scene}
                          onClick={() => onSceneSelect(scene)}
                          onUpdate={(updated) => onSceneUpdate(updated)}
                        />
                      </div>
                    )}
                  </Draggable>
                ))}
              {provided.placeholder}
            </div>
          )}
        </Droppable>
      </DragDropContext>

      {scenes.length === 0 && (
        <div className="flex h-64 items-center justify-center rounded-lg border-2 border-dashed">
          <div className="text-center">
            <p className="text-muted-foreground">No scenes yet</p>
            <Button className="mt-2" size="sm">
              <Plus className="mr-2 h-4 w-4" />
              Add First Scene
            </Button>
          </div>
        </div>
      )}
    </div>
  )
}