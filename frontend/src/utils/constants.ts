export const APP_NAME = 'Website2Video AI'

export const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000'
export const WS_BASE_URL = import.meta.env.VITE_WS_URL || 'ws://localhost:8000'

export const DEFAULT_PAGE_SIZE = 20
export const MAX_PAGE_SIZE = 100

export const VIDEO_RESOLUTIONS = [
  { label: '720p (1280x720)', value: '1280x720' },
  { label: '1080p (1920x1080)', value: '1920x1080' },
  { label: '4K (3840x2160)', value: '3840x2160' },
]

export const VIDEO_QUALITIES = [
  { label: 'Low', value: 'low' },
  { label: 'Medium', value: 'medium' },
  { label: 'High', value: 'high' },
]

export const VIDEO_FPS = [24, 30, 60]

export const EXPORT_FORMATS = [
  { label: 'MP4', value: 'mp4' },
  { label: 'WebM', value: 'webm' },
  { label: 'GIF', value: 'gif' },
  { label: 'AVI', value: 'avi' },
  { label: 'MOV', value: 'mov' },
]

export const SCENE_TYPES = [
  { label: 'Intro', value: 'intro' },
  { label: 'Feature', value: 'feature' },
  { label: 'Benefit', value: 'benefit' },
  { label: 'Testimonial', value: 'testimonial' },
  { label: 'Pricing', value: 'pricing' },
  { label: 'Comparison', value: 'comparison' },
  { label: 'Conclusion', value: 'conclusion' },
  { label: 'Call to Action', value: 'call-to-action' },
]

export const TRANSITION_TYPES = [
  { label: 'Fade', value: 'fade' },
  { label: 'Slide', value: 'slide' },
  { label: 'Zoom', value: 'zoom' },
  { label: 'Flip', value: 'flip' },
  { label: 'Rotate', value: 'rotate' },
]

export const JOB_STATUS_COLORS: Record<string, string> = {
  pending: 'bg-yellow-100 text-yellow-800',
  queued: 'bg-blue-100 text-blue-800',
  running: 'bg-indigo-100 text-indigo-800',
  completed: 'bg-green-100 text-green-800',
  failed: 'bg-red-100 text-red-800',
  cancelled: 'bg-gray-100 text-gray-800',
}

export const VIDEO_STATUS_COLORS: Record<string, string> = {
  draft: 'bg-gray-100 text-gray-800',
  generating: 'bg-yellow-100 text-yellow-800',
  rendering: 'bg-indigo-100 text-indigo-800',
  ready: 'bg-green-100 text-green-800',
  failed: 'bg-red-100 text-red-800',
}