import { create } from 'zustand'
import api from '../api/client'

interface User {
  id: string
  email: string
  full_name: string
  tenant_id: string
  is_superuser: boolean
}

interface AuthStore {
  token: string | null
  user: User | null
  login: (email: string, password: string) => Promise<void>
  logout: () => void
  fetchUser: () => Promise<void>
}

export const useAuthStore = create<AuthStore>((set) => ({
  token: localStorage.getItem('token'),
  user: null,
  
  login: async (email, password) => {
    const { data } = await api.post('/auth/login', { email, password })
    localStorage.setItem('token', data.access_token)
    set({ token: data.access_token })
    
    // Fetch user info
    const userResponse = await api.get('/auth/me')
    set({ user: userResponse.data })
  },
  
  logout: () => {
    localStorage.removeItem('token')
    set({ token: null, user: null })
  },
  
  fetchUser: async () => {
    try {
      const { data } = await api.get('/auth/me')
      set({ user: data })
    } catch (error) {
      console.error('Failed to fetch user:', error)
    }
  },
}))
