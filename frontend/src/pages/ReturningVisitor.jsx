import { useState } from 'react'
import { FiKey } from 'react-icons/fi'
import { Link, useNavigate } from 'react-router-dom'
import { useVisitor } from '../hooks/useVisitor.js'
import { getApiErrorMessage } from '../services/api.js'

export default function ReturningVisitor() {
  const { verifyVisitor } = useVisitor()
  const navigate = useNavigate()
  const [accessCode, setAccessCode] = useState('')
  const [error, setError] = useState('')
  const [submitting, setSubmitting] = useState(false)

  async function submit(event) {
    event.preventDefault()
    setError('')
    setSubmitting(true)
    try {
      await verifyVisitor(accessCode)
      navigate('/dashboard')
    } catch (requestError) {
      setError(getApiErrorMessage(requestError, 'Could not verify that code.'))
    } finally {
      setSubmitting(false)
    }
  }

  function updateCode(value) {
    const characters = value.toUpperCase().replace(/[^A-HJ-NP-Z2-9]/g, '').slice(0, 16)
    setAccessCode(characters.match(/.{1,4}/g)?.join('-') || '')
  }

  return (
    <div className="auth-page">
      <div className="auth-heading">
        <span className="eyebrow">
          <FiKey aria-hidden="true" /> Welcome back
        </span>
        <h1>Your story is right where you left it.</h1>
        <p>
          Enter the access code you received when you registered to see your
          profile and photos.
        </p>
        <div className="auth-aside-note">
          Your code is private. It is used to find your profile and is never
          displayed in a page address.
        </div>
      </div>

      <div className="form-card">
        <h2 className="form-card-title">Return to your photos</h2>
        {error && (
          <div className="alert-message" role="alert">
            {error}
          </div>
        )}
        <form onSubmit={submit}>
          <label className="field-label" htmlFor="visitor-access-code">
            Visitor access code
          </label>
          <input
            autoCapitalize="characters"
            autoComplete="off"
            className="form-control-custom"
            id="visitor-access-code"
            maxLength={19}
            onChange={(event) => updateCode(event.target.value)}
            placeholder="XXXX-XXXX-XXXX-XXXX"
            required
            value={accessCode}
          />
          <span className="form-hint">
            The code is made up of 16 letters and numbers.
          </span>
          <button
            className="button-primary form-submit"
            disabled={submitting || accessCode.replaceAll('-', '').length !== 16}
            style={{ marginTop: 23 }}
            type="submit"
          >
            {submitting ? 'Checking your code…' : 'Access my photos'}
          </button>
        </form>
        <div className="form-footer">
          New to Memory Lane? <Link to="/register">Create a profile</Link>
        </div>
      </div>
    </div>
  )
}
