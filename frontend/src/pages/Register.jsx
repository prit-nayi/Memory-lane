import { useState } from 'react'
import { FiCheck, FiCopy, FiHeart } from 'react-icons/fi'
import { Link } from 'react-router-dom'
import { getApiErrorMessage } from '../services/api.js'
import { useVisitor } from '../hooks/useVisitor.js'

export default function Register() {
  const { registerVisitor } = useVisitor()
  const [name, setName] = useState('')
  const [consent, setConsent] = useState(false)
  const [registration, setRegistration] = useState(null)
  const [error, setError] = useState('')
  const [submitting, setSubmitting] = useState(false)
  const [copied, setCopied] = useState(false)

  async function submit(event) {
    event.preventDefault()
    setError('')
    setSubmitting(true)
    try {
      const result = await registerVisitor({ name, consent })
      setRegistration(result)
    } catch (requestError) {
      setError(
        getApiErrorMessage(requestError, 'Could not create your visitor account.'),
      )
    } finally {
      setSubmitting(false)
    }
  }

  async function copyCode() {
    try {
      await navigator.clipboard.writeText(registration.access_code)
      setCopied(true)
    } catch {
      setError('Copy was unavailable. Please write down your access code.')
    }
  }

  return (
    <div className="auth-page">
      <div className="auth-heading">
        <span className="eyebrow">
          <FiHeart aria-hidden="true" /> Start your Memory Lane
        </span>
        <h1>Your memories belong here.</h1>
        <p>
          Create your visitor profile to share photos and keep them connected to
          you whenever you return.
        </p>
        <div className="auth-aside-note">
          After registering, save your unique access code somewhere safe. It is
          the key to your photos.
        </div>
      </div>

      <div className="form-card">
        {!registration ? (
          <>
            <h2 className="form-card-title">Create visitor profile</h2>
            {error && (
              <div className="alert-message" role="alert">
                {error}
              </div>
            )}
            <form onSubmit={submit}>
              <label className="field-label" htmlFor="visitor-name">
                Your name
              </label>
              <input
                autoComplete="name"
                className="form-control-custom"
                id="visitor-name"
                maxLength={100}
                onChange={(event) => setName(event.target.value)}
                placeholder="e.g. Jamie Parker"
                required
                value={name}
              />
              <span className="form-hint">
                Use the name you would like to see on your visitor profile.
              </span>

              <label className="consent-check">
                <input
                  checked={consent}
                  onChange={(event) => setConsent(event.target.checked)}
                  required
                  type="checkbox"
                />
                <span>
                  I agree to display my uploaded photos in my personal Memory
                  Lane slideshow. Only someone with my access code can view them.
                </span>
              </label>

              <button
                className="button-primary form-submit"
                disabled={submitting || !consent}
                type="submit"
              >
                {submitting ? 'Creating your profile…' : 'Create my profile'}
              </button>
            </form>
            <div className="form-footer">
              Already have an access code? <Link to="/returning">Come back in</Link>
            </div>
          </>
        ) : (
          <>
            <div className="alert-message success" role="status">
              <FiCheck aria-hidden="true" /> Your visitor profile is ready.
            </div>
            <h2 className="form-card-title">Keep this access code safe</h2>
            <p className="form-hint">
              You will need this code to return to your profile. It is shown
              here only during registration.
            </p>
            <div className="access-code-box">
              <div className="access-code-label">Your personal access code</div>
              <code className="access-code-value">{registration.access_code}</code>
              <div className="code-actions">
                <button
                  className="button-secondary"
                  onClick={copyCode}
                  type="button"
                >
                  {copied ? <FiCheck aria-hidden="true" /> : <FiCopy aria-hidden="true" />}
                  {copied ? 'Copied' : 'Copy code'}
                </button>
              </div>
            </div>
            {error && (
              <div className="alert-message" role="alert">
                {error}
              </div>
            )}
            <Link className="button-primary form-submit" to="/upload">
              Continue to photo upload
            </Link>
          </>
        )}
      </div>
    </div>
  )
}
