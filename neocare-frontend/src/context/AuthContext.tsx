import { createContext, useContext, useState, useEffect, useMemo, type ReactNode } from 'react'
import apiClient from '../api/clients'
import type { User } from '../types'

interface AuthContextType{
  user: User | null
  loading: boolean
  login: (email: string, password: string) => Promise<void>
  logout: () => void
}

const AuthContext = createContext<AuthContextType>(null!)

export function AuthProvider({ children }: { children: ReactNode}) {
  const [user, setUser] = useState<User | null>(null)
  const[loading, setLoading] = useState(true)

  useEffect(() => {
    const token = localStorage.getItem('access_token')
    if (!token) { 
      setLoading(false); 
      return 
    }
    apiClient.get('/users/me')
      .then((res) => setUser(res.data))
      .catch(() => {
        localStorage.removeItem('access_token')
        setUser(null)
      })
      .finally(() => setLoading(false))
  }, [])

  const login = async (email:string, password: string) => {
    const form = new URLSearchParams()
    form.set('username', email)
    form.set('password', password)
    const res = await apiClient.post('/auth/login', form, {
      headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
    })
    localStorage.setItem('access_token', res.data.access_token)
    const me = await apiClient.get('/users/me')
    setUser(me.data)
  }

  const logout = () => {
    localStorage.removeItem('access_token')
    setUser(null)
  }

  const value= useMemo(() => ({ user, loading, login, logout }), [user, loading])
  
  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>
}

export const useAuth = () => useContext(AuthContext)