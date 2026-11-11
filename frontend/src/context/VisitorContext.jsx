import { useCallback, useEffect, useMemo, useState } from 'react'
import { VisitorContext } from './visitorContext.js'
import { getApiErrorMessage } from '../services/api.js'
import {
  getCurrentVisitor,
  registerVisitor as requestRegistration,
  verifyVisitor as requestVerification,
} from '../services/visitorService.js'

const ACCESS_CODE_KEY = 'memory-lane.access-code'

export function VisitorProvider({ children }) {
  const [visitor, setVisitor] = useState(null)
  const [accessCode, setAccessCode] = useState('')
  const [loading, setLoading] = useState(() =>
    Boolean(sessionStorage.getItem(ACCESS_CODE_KEY)),
  )
  const [sessionError, setSessionError] = useState('')

  const saveSession = useCallback((profile, code) => {
    sessionStorage.setItem(ACCESS_CODE_KEY, code)
    setVisitor(profile)
    setAccessCode(code)
    setSessionError('')
  }, [])

  const clearSession = useCallback(() => {
    sessionStorage.removeItem(ACCESS_CODE_KEY)
    setVisitor(null)
    setAccessCode('')
    setSessionError('')
  }, [])

  useEffect(() => {
    let active = true
    const storedCode = sessionStorage.getItem(ACCESS_CODE_KEY)

    if (!storedCode) {
      return () => {
        active = false
      }
    }

    getCurrentVisitor(storedCode)
      .then((profile) => {
        if (active) {
          setVisitor(profile)
          setAccessCode(storedCode)
        }
      })
      .catch((error) => {
        if (!active) {
          return
        }
        if (error.response?.status === 401 || error.response?.status === 422) {
          sessionStorage.removeItem(ACCESS_CODE_KEY)
          return
        }
        setSessionError(
          getApiErrorMessage(error, 'Could not restore your visitor session.'),
        )
      })
      .finally(() => {
        if (active) {
          setLoading(false)
        }
      })

    return () => {
      active = false
    }
  }, [])

  const registerVisitor = useCallback(
    async (details) => {
      const response = await requestRegistration(details)
      const { access_code: code, ...profile } = response
      saveSession(profile, code)
      return response
    },
    [saveSession],
  )

  const verifyVisitor = useCallback(
    async (code) => {
      const profile = await requestVerification(code)
      saveSession(profile, code.replace(/[\s-]/g, '').toUpperCase())
      return profile
    },
    [saveSession],
  )

  const value = useMemo(
    () => ({
      visitor,
      accessCode,
      loading,
      sessionError,
      registerVisitor,
      verifyVisitor,
      clearSession,
    }),
    [
      visitor,
      accessCode,
      loading,
      sessionError,
      registerVisitor,
      verifyVisitor,
      clearSession,
    ],
  )

  return <VisitorContext.Provider value={value}>{children}</VisitorContext.Provider>
}
