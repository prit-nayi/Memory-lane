import { useState } from 'react'
import { Navigate, useNavigate } from 'react-router-dom'
import { useAdmin } from '../hooks/useAdmin.js'
import { getApiErrorMessage } from '../services/api.js'

export default function AdminLogin() {
  const { token, login } = useAdmin()
  const navigate = useNavigate()
  const [username, setUsername] = useState('')
  const [password, setPassword] = useState('')
  const [error, setError] = useState('')
  const [submitting, setSubmitting] = useState(false)

  if (token) {
    return <Navigate replace to="/admin" />
  }

  async function submit(event) {
    event.preventDefault()
    setError('')
    setSubmitting(true)
    try {
      await login(username, password)
      navigate('/admin', { replace: true })
    } catch (requestError) {
      setError(getApiErrorMessage(requestError, 'Could not sign in as admin.'))
    } finally {
      setSubmitting(false)
    }
  }

  return (
    <section className="admin-login-page">
      <form className="admin-login-card" onSubmit={submit}>
        <span className="eyebrow">Memory Lane</span>
        <h1>Administrator sign in</h1>
        <p>Manage visitors, photos, and slideshow defaults.</p>
        {error && <div className="alert-message" role="alert">{error}</div>}
        <label className="field-label" htmlFor="admin-username">Username</label>
        <input
          autoComplete="username"
          className="form-control-custom"
          id="admin-username"
          onChange={(event) => setUsername(event.target.value)}
          required
          value={username}
        />
        <label className="field-label" htmlFor="admin-password">Password</label>
        <input
          autoComplete="current-password"
          className="form-control-custom"
          id="admin-password"
          onChange={(event) => setPassword(event.target.value)}
          required
          type="password"
          value={password}
        />
        <button className="button-primary form-submit" disabled={submitting} type="submit">
          {submitting ? 'Signing in…' : 'Sign in'}
        </button>
      </form>
    </section>
  )
}
