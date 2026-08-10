import { useState } from 'react'
import { Palette, Type, Layout, Sparkles } from 'lucide-react'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Select } from '@/components/ui/select'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'

interface StyleEditorProps {
  style: {
    theme: string
    font: string
    colors: {
      primary: string
      secondary: string
      accent: string
      background: string
      text: string
    }
    animations: {
      transition: string
      duration: number
      camera_pan: boolean
      zoom_effect: boolean
      highlight_effect: boolean
      cursor_effect: boolean
    }
  }
  onStyleChange: (style: any) => void
}

export function StyleEditor({ style, onStyleChange }: StyleEditorProps) {
  const [activeTab, setActiveTab] = useState('theme')

  const themes = [
    'professional',
    'modern',
    'minimalist',
    'playful',
    'corporate',
    'creative',
  ]

  const fonts = [
    'Inter',
    'Roboto',
    'Open Sans',
    'Lato',
    'Montserrat',
    'Poppins',
  ]

  const transitions = [
    'fade',
    'slide',
    'zoom',
    'flip',
    'rotate',
    'none',
  ]

  const handleColorChange = (key: string, value: string) => {
    onStyleChange({
      ...style,
      colors: {
        ...style.colors,
        [key]: value,
      },
    })
  }

  const handleAnimationToggle = (key: string) => {
    onStyleChange({
      ...style,
      animations: {
        ...style.animations,
        [key]: !style.animations[key as keyof typeof style.animations],
      },
    })
  }

  return (
    <div className="space-y-4 p-4">
      <div className="flex items-center justify-between">
        <h2 className="text-lg font-semibold">Style Editor</h2>
        <Button size="sm" variant="outline">
          <Sparkles className="mr-2 h-4 w-4" />
          Auto-Enhance
        </Button>
      </div>

      <Tabs value={activeTab} onValueChange={setActiveTab}>
        <TabsList className="grid w-full grid-cols-4">
          <TabsTrigger value="theme">
            <Palette className="mr-2 h-4 w-4" />
            Theme
          </TabsTrigger>
          <TabsTrigger value="colors">
            <Palette className="mr-2 h-4 w-4" />
            Colors
          </TabsTrigger>
          <TabsTrigger value="typography">
            <Type className="mr-2 h-4 w-4" />
            Typography
          </TabsTrigger>
          <TabsTrigger value="animations">
            <Layout className="mr-2 h-4 w-4" />
            Animations
          </TabsTrigger>
        </TabsList>

        <TabsContent value="theme" className="space-y-4">
          <div>
            <Label>Theme</Label>
            <Select
              value={style.theme}
              onValueChange={(value) =>
                onStyleChange({ ...style, theme: value })
              }
            >
              {themes.map((theme) => (
                <option key={theme} value={theme}>
                  {theme.charAt(0).toUpperCase() + theme.slice(1)}
                </option>
              ))}
            </Select>
          </div>

          <div className="grid grid-cols-2 gap-2">
            {themes.map((theme) => (
              <button
                key={theme}
                className={`rounded-lg border p-2 text-sm capitalize transition-colors ${
                  style.theme === theme
                    ? 'border-primary bg-primary/10'
                    : 'hover:bg-secondary'
                }`}
                onClick={() => onStyleChange({ ...style, theme })}
              >
                {theme}
              </button>
            ))}
          </div>
        </TabsContent>

        <TabsContent value="colors" className="space-y-4">
          <div className="grid gap-4 md:grid-cols-2">
            <div>
              <Label>Primary</Label>
              <div className="flex items-center space-x-2">
                <input
                  type="color"
                  value={style.colors.primary}
                  onChange={(e) => handleColorChange('primary', e.target.value)}
                  className="h-10 w-10 cursor-pointer rounded border"
                />
                <Input
                  value={style.colors.primary}
                  onChange={(e) => handleColorChange('primary', e.target.value)}
                  className="flex-1"
                />
              </div>
            </div>

            <div>
              <Label>Secondary</Label>
              <div className="flex items-center space-x-2">
                <input
                  type="color"
                  value={style.colors.secondary}
                  onChange={(e) => handleColorChange('secondary', e.target.value)}
                  className="h-10 w-10 cursor-pointer rounded border"
                />
                <Input
                  value={style.colors.secondary}
                  onChange={(e) => handleColorChange('secondary', e.target.value)}
                  className="flex-1"
                />
              </div>
            </div>

            <div>
              <Label>Accent</Label>
              <div className="flex items-center space-x-2">
                <input
                  type="color"
                  value={style.colors.accent}
                  onChange={(e) => handleColorChange('accent', e.target.value)}
                  className="h-10 w-10 cursor-pointer rounded border"
                />
                <Input
                  value={style.colors.accent}
                  onChange={(e) => handleColorChange('accent', e.target.value)}
                  className="flex-1"
                />
              </div>
            </div>

            <div>
              <Label>Background</Label>
              <div className="flex items-center space-x-2">
                <input
                  type="color"
                  value={style.colors.background}
                  onChange={(e) => handleColorChange('background', e.target.value)}
                  className="h-10 w-10 cursor-pointer rounded border"
                />
                <Input
                  value={style.colors.background}
                  onChange={(e) => handleColorChange('background', e.target.value)}
                  className="flex-1"
                />
              </div>
            </div>
          </div>
        </TabsContent>

        <TabsContent value="typography" className="space-y-4">
          <div>
            <Label>Font</Label>
            <Select
              value={style.font}
              onValueChange={(value) =>
                onStyleChange({ ...style, font: value })
              }
            >
              {fonts.map((font) => (
                <option key={font} value={font}>
                  {font}
                </option>
              ))}
            </Select>
          </div>

          <div className="rounded bg-secondary p-4">
            <p style={{ fontFamily: style.font }} className="text-lg">
              The quick brown fox jumps over the lazy dog
            </p>
            <p className="text-sm text-muted-foreground">Preview</p>
          </div>
        </TabsContent>

        <TabsContent value="animations" className="space-y-4">
          <div>
            <Label>Transition</Label>
            <Select
              value={style.animations.transition}
              onValueChange={(value) =>
                onStyleChange({
                  ...style,
                  animations: { ...style.animations, transition: value },
                })
              }
            >
              {transitions.map((transition) => (
                <option key={transition} value={transition}>
                  {transition.charAt(0).toUpperCase() + transition.slice(1)}
                </option>
              ))}
            </Select>
          </div>

          <div>
            <Label>Transition Duration (seconds)</Label>
            <Input
              type="number"
              value={style.animations.duration}
              onChange={(e) =>
                onStyleChange({
                  ...style,
                  animations: {
                    ...style.animations,
                    duration: parseFloat(e.target.value) || 0.5,
                  },
                })
              }
              min={0.1}
              max={5}
              step={0.1}
            />
          </div>

          <div className="space-y-2">
            <Label>Effects</Label>
            <div className="space-y-1">
              <label className="flex items-center space-x-2">
                <input
                  type="checkbox"
                  checked={style.animations.camera_pan}
                  onChange={() => handleAnimationToggle('camera_pan')}
                />
                <span>Camera Pan</span>
              </label>
              <label className="flex items-center space-x-2">
                <input
                  type="checkbox"
                  checked={style.animations.zoom_effect}
                  onChange={() => handleAnimationToggle('zoom_effect')}
                />
                <span>Zoom Effect</span>
              </label>
              <label className="flex items-center space-x-2">
                <input
                  type="checkbox"
                  checked={style.animations.highlight_effect}
                  onChange={() => handleAnimationToggle('highlight_effect')}
                />
                <span>Highlight Effect</span>
              </label>
              <label className="flex items-center space-x-2">
                <input
                  type="checkbox"
                  checked={style.animations.cursor_effect}
                  onChange={() => handleAnimationToggle('cursor_effect')}
                />
                <span>Cursor Effect</span>
              </label>
            </div>
          </div>
        </TabsContent>
      </Tabs>
    </div>
  )
}