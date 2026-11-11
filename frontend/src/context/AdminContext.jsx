import { useCallback, useMemo, useState } from 'react'
import { AdminContext } from './adminContext.js'
import { loginAdmin as requestAdminLogin } from '../services/adminService.js'

const ADMIN_SESSION_KEY = 'memory-lane.admin-session'

function readSession() {
  try {
    const stored = JSON.parse(sessionStorage.getItem(ADMIN_SESSION_KEY) || 'null')
    if (stored?.token && stored.expiresAt > Date.now()) {
      return stored
    }
  } catch {
    sessionStorage.removeItem(ADMIN_SESSION_KEY)
  }
  sessionStorage.removeItem(ADMIN_SESSION_KEY)
  return null
}

export function AdminProvider({ children }) {
  const [session, setSession] = useState(readSession)

  const login = useCallback(async (username, password) => {
    const result = await requestAdminLogin(username, password)
    const nextSession = {
      token: result.access_token,
      expiresAt: Date.now() + result.expires_in * 1000,
    }
    sessionStorage.setItem(ADMIN_SESSION_KEY, JSON.stringify(nextSession))
    setSession(nextSession)
  }, [])

  const logout = useCallback(() => {
    sessionStorage.removeItem(ADMIN_SESSION_KEY)
    setSession(null)
  }, [])

  const value = useMemo(
    () => ({ token: session?.token || '', login, logout }),
    [session, login, logout],
  )

  return <AdminContext.Provider value={value}>{children}</AdminContext.Provider>
}
