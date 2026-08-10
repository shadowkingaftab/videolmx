export interface Job {
  id: string
  type: 'crawl' | 'analysis' | 'script' | 'narration' | 'render' | 'export'
  status: 'pending' | 'queued' | 'running' | 'completed' | 'failed' | 'cancelled' | 'retrying'
  progress: number
  error_message?: string
  error_details?: Record<string, any>
  started_at?: string
  completed_at?: string
  failed_at?: string
  created_at: string
  updated_at: string
  results?: Record<string, any>
}

export interface CrawlJob extends Job {
  type: 'crawl'
  website_id: string
  max_pages: number
  max_depth: number
  include_assets: boolean
  respect_robots: boolean
  pages_crawled: number
  total_pages: number
  assets_collected: number
}

export interface AnalysisJob extends Job {
  type: 'analysis'
  website_id: string
  analysis_type: 'full' | 'quick' | 'custom'
  depth: 'shallow' | 'standard' | 'deep'
  semantic_understanding?: Record<string, any>
  ui_analysis?: Record<string, any>
  feature_extraction?: Record<string, any>
  navigation_graph?: Record<string, any>
  value_proposition?: Record<string, any>
  confidence_scores?: Record<string, number>
  summary?: string
}

export interface ScriptJob extends Job {
  type: 'script'
  script_id: string
  tone: string
  length: 'short' | 'medium' | 'long'
  include_captions: boolean
}

export interface NarrationJob extends Job {
  type: 'narration'
  narration_id: string
  voice_id: string
  speed: number
  pitch: number
  emotion: string
}

export interface RenderJob extends Job {
  type: 'render'
  video_id: string
  resolution: string
  fps: number
  quality: string
  include_captions: boolean
  include_background_music: boolean
}

export interface ExportJob extends Job {
  type: 'export'
  export_id: string
  format: string
  quality: string
  include_watermark: boolean
}

export type AnyJob =
  | CrawlJob
  | AnalysisJob
  | ScriptJob
  | NarrationJob
  | RenderJob
  | ExportJob

export interface JobProgress {
  job_id: string
  progress: number
  status: string
  message?: string
}

export interface JobResult {
  job_id: string
  status: string
  result?: Record<string, any>
  error?: string
}