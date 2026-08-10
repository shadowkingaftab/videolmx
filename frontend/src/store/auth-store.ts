import { create } from 'zustand'
import { persist } from 'zustand/middleware'

interface AuthState {
  user: {
    id: string
    email: string
    full_name: string
    is_admin: boolean
    plan: string
  } | null
  isAuthenticated: boolean
  setUser: (user: AuthState['user']) => void
  logout: () => void
}

export const useAuthStore = create<AuthState>()(
  persist(
    (set) => ({
      user: null,
      isAuthenticated: false,
      setUser: (user) => set({ user, isAuthenticated: !!user }),
      logout: () => set({ user: null, isAuthenticated: false }),
    }),
    {
      name: 'auth-storage',
    }
  )
)