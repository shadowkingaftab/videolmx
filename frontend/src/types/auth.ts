export interface User {
  id: string
  email: string
  full_name: string
  avatar_url?: string
  is_active: boolean
  is_admin: boolean
  is_verified: boolean
  plan: 'free' | 'pro' | 'business' | 'enterprise'
  plan_expires_at?: string
  last_login_at?: string
  created_at: string
  updated_at: string
}

export interface LoginRequest {
  email: string
  password: string
}

export interface LoginResponse {
  access_token: string
  refresh_token: string
  token_type: string
  user_id: string
  email: string
  full_name: string
}

export interface RegisterRequest {
  email: string
  password: string
  full_name: string
}

export interface RegisterResponse extends LoginResponse {}

export interface RefreshTokenRequest {
  refresh_token: string
}

export interface RefreshTokenResponse {
  access_token: string
  refresh_token: string
}

export interface ChangePasswordRequest {
  current_password: string
  new_password: string
}

export interface PasswordResetRequest {
  email: string
}

export interface PasswordResetConfirmRequest {
  token: string
  new_password: string
}