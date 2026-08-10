export interface ApiResponse<T> {
  data: T
  message?: string
  status: number
}

export interface ApiError {
  code: string
  message: string
  details?: Record<string, any>
  status_code: number
}

export interface PaginatedResponse<T> {
  items: T[]
  total: number
  page: number
  page_size: number
  pages: number
}

export interface PaginationParams {
  page?: number
  page_size?: number
  sort_by?: string
  sort_order?: 'asc' | 'desc'
}

export interface FilterParams {
  search?: string
  status?: string
  date_from?: string
  date_to?: string
}

export type RequestParams = PaginationParams & FilterParams