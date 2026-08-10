import { useState } from 'react'
import { Edit2, Save, Sparkles } from 'lucide-react'
import { Button } from '@/components/ui/button'
import { Textarea } from '@/components/ui/textarea'

interface ScriptEditorProps {
  script?: {
    content?: string
    scenes?: Array<{ title: string; content: string }>
  }
  onUpdate?: (content: string) => void
}

export function ScriptEditor({ script, onUpdate }: ScriptEditorProps) {
  const [isEditing, setIsEditing] = useState(false)
  const [content, setContent] = useState(script?.content || '')

  const handleSave = () => {
    onUpdate?.(content)
    setIsEditing(false)
  }

  const handleGenerate = () => {
    // Trigger AI generation
  }

  return (
    <div className="space-y-4 p-4">
      <div className="flex items-center justify-between">
        <h2 className="text-lg font-semibold">Script</h2>
        <div className="flex space-x-2">
          <Button size="sm" variant="outline" onClick={handleGenerate}>
            <Sparkles className="mr-2 h-4 w-4" />
            Generate
          </Button>
          {isEditing ? (
            <Button size="sm" onClick={handleSave}>
              <Save className="mr-2 h-4 w-4" />
              Save
            </Button>
          ) : (
            <Button size="sm" variant="outline" onClick={() => setIsEditing(true)}>
              <Edit2 className="mr-2 h-4 w-4" />
              Edit
            </Button>
          )}
        </div>
      </div>

      {isEditing ? (
        <Textarea
          value={content}
          onChange={(e) => setContent(e.target.value)}
          rows={20}
          className="font-mono"
        />
      ) : (
        <div className="prose prose-sm max-w-none rounded-lg border bg-card p-4">
          {content ? (
            <div className="whitespace-pre-wrap">{content}</div>
          ) : (
            <p className="text-muted-foreground">No script content yet</p>
          )}
        </div>
      )}

      {/* Scene breakdown */}
      {script?.scenes && script.scenes.length > 0 && (
        <div className="mt-6">
          <h3 className="mb-2 text-sm font-medium text-muted-foreground">Scenes</h3>
          <div className="space-y-2">
            {script.scenes.map((scene, index) => (
              <div key={index} className="rounded border p-3">
                <p className="font-medium">{scene.title}</p>
                <p className="text-sm text-muted-foreground">{scene.content}</p>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  )
}