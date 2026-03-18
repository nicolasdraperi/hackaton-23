import { createContext, useContext, useState, useEffect } from 'react'
import api from '../api'

const AuthCtx = createContext(null)

export function AuthProvider({ children }) {
  const [user, setUser] = useState(null)
  const [ready, setReady] = useState(false)

  useEffect(() => {
    api.me()
      .then(setUser)
      .catch(() => setUser(null))
      .finally(() => setReady(true))
  }, [])

  const login  = async (u, p) => { const d = await api.login(u, p); setUser(d.user); return d.user }
  const logout = async ()     => { await api.logout().catch(() => {}); setUser(null) }
  const patch  = (u)          => setUser(x => ({ ...x, ...u }))

  return (
    <AuthCtx.Provider value={{ user, ready, login, logout, patch, setUser }}>
      {children}
    </AuthCtx.Provider>
  )
}

export const useAuth = () => useContext(AuthCtx)
export const isAdmin = (u) => u?.role === 'admin' || u?.is_superuser
