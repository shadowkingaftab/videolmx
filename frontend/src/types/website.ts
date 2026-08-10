export interface Website {
  id: string
  project_id: string
  url: string
  title?: string
  description?: string
  status: 'pending' | 'crawling' | 'analyzing' | 'completed' | 'failed'
  crawled_at?: string
  analyzed_at?: string
  digital_twin?: DigitalTwin
  metadata?: Record<string, any>
  is_active: boolean
  created_at: string
  updated_at: string
}

export interface DigitalTwin {
  pages: DigitalTwinPage[]
  components: DigitalTwinComponent[]
  navigation: DigitalTwinNavigation
  features: string[]
  color_palette: string[]
  typography: DigitalTwinTypography
  layout: DigitalTwinLayout
}

export interface DigitalTwinPage {
  url: string
  title: string
  content: string
  images: string[]
  links: string[]
}

export interface DigitalTwinComponent {
  id: string
  type: string
  content: any
  position: { x: number; y: number }
}

export interface DigitalTwinNavigation {
  items: Array<{ label: string; url: string }>
  structure: Record<string, any>
}

export interface DigitalTwinTypography {
  headings: Record<string, { font: string; size: string; weight: string }>
  body: { font: string; size: string; line_height: string }
}

export interface DigitalTwinLayout {
  sections: Array<{ type: string; order: number }>
  grid: { columns: number; rows: number }
}

export interface CreateWebsiteRequest {
  project_id: string
  url: string
}

export interface UpdateWebsiteRequest {
  title?: string
  description?: string
  status?: string
  metadata?: Record<string, any>
}

export interface WebsiteAnalysisRequest {
  max_pages?: number
  depth?: number
  include_assets?: boolean
}