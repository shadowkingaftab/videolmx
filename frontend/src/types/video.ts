export interface Video {
  id: string
  project_id: string
  name: string
  description?: string
  storyboard_id?: string
  script_id?: string
  narration_id?: string
  status: 'draft' | 'generating' | 'rendering' | 'ready' | 'failed' | 'expired'
  progress: number
  resolution: string
  fps: number
  quality: string
  include_captions: boolean
  include_background_music: boolean
  background_music_volume: number
  duration?: number
  file_size?: number
  file_url?: string
  storage_key?: string
  preview_url?: string
  thumbnail_url?: string
  render_job_id?: string
  render_duration?: number
  render_started_at?: string
  render_completed_at?: string
  error_message?: string
  error_details?: Record<string, any>
  metadata?: Record<string, any>
  view_count: number
  share_count: number
  created_at: string
  updated_at: string
}

export interface CreateVideoRequest {
  project_id: string
  name: string
  description?: string
  storyboard_id?: string
  script_id?: string
  narration_id?: string
}

export interface UpdateVideoRequest {
  name?: string
  description?: string
  status?: 'draft' | 'generating' | 'rendering' | 'ready' | 'failed'
  resolution?: string
  fps?: number
  quality?: string
  include_captions?: boolean
  include_background_music?: boolean
  background_music_volume?: number
  metadata?: Record<string, any>
}

export interface RenderVideoRequest {
  resolution?: string
  fps?: number
  quality?: string
  include_captions?: boolean
  include_background_music?: boolean
}

export interface VideoStatus {
  status: string
  progress: number
  duration?: number
  render_started_at?: string
  render_completed_at?: string
}

export interface Export {
  id: string
  video_id: string
  format: 'mp4' | 'webm' | 'gif' | 'avi' | 'mov'
  quality: 'low' | 'medium' | 'high'
  status: 'pending' | 'exporting' | 'completed' | 'failed'
  progress: number
  include_watermark: boolean
  include_metadata: boolean
  file_size?: number
  file_url?: string
  storage_key?: string
  download_count: number
  started_at?: string
  completed_at?: string
  expires_at?: string
  error_message?: string
  created_at: string
  updated_at: string
}

export interface ExportVideoRequest {
  format: 'mp4' | 'webm' | 'gif' | 'avi' | 'mov'
  quality?: 'low' | 'medium' | 'high'
  include_watermark?: boolean
}