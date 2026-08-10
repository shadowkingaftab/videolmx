import apiClient from './client'

interface LoginResponse {
  access_token: string
  refresh_token: string
  token_type: string
  user_id: string
  email: string
  full_name: string
}

interface User {
  id: string
  email: string
  full_name: string
  is_active: boolean
  is_admin: boolean
  plan: string
  created_at: string
}

export const authApi = {
  login: async (email: string, password: string): Promise<LoginResponse> => {
    const response = await apiClient.post('/api/v1/auth/login', { email, password })
    return response.data
  },

  register: async (email: string, password: string, fullName: string): Promise<LoginResponse> => {
    const response = await apiClient.post('/api/v1/auth/register', {
      email,
      password,
      full_name: fullName,
    })
    return response.data
  },

  logout: async (): Promise<void> => {
    await apiClient.post('/api/v1/auth/logout')
  },

  getCurrentUser: async (): Promise<User> => {
    const response = await apiClient.get('/api/v1/auth/me')
    return response.data
  },

  refreshToken: async (refreshToken: string): Promise<{ access_token: string; refresh_token: string }> => {
    const response = await apiClient.post('/api/v1/auth/refresh', {
      refresh_token: refreshToken,
    })
    return response.data
  },

  changePassword: async (currentPassword: string, newPassword: string): Promise<void> => {
    await apiClient.post('/api/v1/auth/change-password', {
      current_password: currentPassword,
      new_password: newPassword,
    })
  },

  requestPasswordReset: async (email: string): Promise<void> => {
    await apiClient.post('/api/v1/auth/password-reset', { email })
  },

  confirmPasswordReset: async (token: string, newPassword: string): Promise<void> => {
    await apiClient.post('/api/v1/auth/password-reset/confirm', {
      token,
      new_password: newPassword,
    })
  },
}