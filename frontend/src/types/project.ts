export interface Project {
  id: string
  user_id: string
  name: string
  description?: string
  status: 'active' | 'archived' | 'deleted'
  settings?: Record<string, any>
  created_at: string
  updated_at: string
  deleted_at?: string
  video_count?: number
  website_count?: number
}

export interface CreateProjectRequest {
  name: string
  description?: string
}

export interface UpdateProjectRequest {
  name?: string
  description?: string
  status?: 'active' | 'archived' | 'deleted'
  settings?: Record<string, any>
}

export interface ProjectStats {
  total_websites: number
  total_videos: number
  total_assets: number
  total_scenes: number
}