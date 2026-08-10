import { createContext, useState, useEffect, ReactNode } from 'react'
import { authApi } from '@/api/auth'
import { toast } from 'react-hot-toast'

interface User {
  id: string
  email: string
  full_name: string
  is_active: boolean
  is_admin: boolean
  plan: string
  created_at: string
}

interface AuthContextType {
  user: User | null
  isLoading: boolean
  login: (email: string, password: string) => Promise<void>
  signup: (email: string, password: string, fullName: string) => Promise<void>
  logout: () => Promise<void>
  updateUser: (user: User) => void
}

export const AuthContext = createContext<AuthContextType | null>(null)

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<User | null>(null)
  const [isLoading, setIsLoading] = useState(true)

  useEffect(() => {
    const loadUser = async () => {
      const token = localStorage.getItem('access_token')
      if (!token) {
        setIsLoading(false)
        return
      }

      try {
        const userData = await authApi.getCurrentUser()
        setUser(userData)
      } catch (error) {
        localStorage.removeItem('access_token')
        localStorage.removeItem('refresh_token')
        localStorage.removeItem('user')
      } finally {
        setIsLoading(false)
      }
    }

    loadUser()
  }, [])

  const login = async (email: string, password: string) => {
    try {
      const response = await authApi.login(email, password)
      localStorage.setItem('access_token', response.access_token)
      localStorage.setItem('refresh_token', response.refresh_token)
      
      const userData = await authApi.getCurrentUser()
      setUser(userData)
      localStorage.setItem('user', JSON.stringify(userData))
      
      toast.success('Welcome back!')
    } catch (error) {
      toast.error('Invalid credentials')
      throw error
    }
  }

  const signup = async (email: string, password: string, fullName: string) => {
    try {
      const response = await authApi.register(email, password, fullName)
      localStorage.setItem('access_token', response.access_token)
      localStorage.setItem('refresh_token', response.refresh_token)
      
      const userData = await authApi.getCurrentUser()
      setUser(userData)
      localStorage.setItem('user', JSON.stringify(userData))
      
      toast.success('Account created successfully!')
    } catch (error) {
      toast.error('Failed to create account')
      throw error
    }
  }

  const logout = async () => {
    try {
      await authApi.logout()
    } catch (error) {
      // Ignore logout errors
    } finally {
      localStorage.removeItem('access_token')
      localStorage.removeItem('refresh_token')
      localStorage.removeItem('user')
      setUser(null)
      toast.success('Logged out')
    }
  }

  const updateUser = (updatedUser: User) => {
    setUser(updatedUser)
    localStorage.setItem('user', JSON.stringify(updatedUser))
  }

  const value = {
    user,
    isLoading,
    login,
    signup,
    logout,
    updateUser,
  }

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>
}