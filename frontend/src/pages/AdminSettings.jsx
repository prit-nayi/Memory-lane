import { useEffect, useState } from 'react'
import AdminLayout from '../components/AdminLayout.jsx'
import { useAdmin } from '../hooks/useAdmin.js'
import { getApiErrorMessage } from '../services/api.js'
import { getAdminSettings, updateAdminSettings } from '../services/adminService.js'

const INITIAL_SETTINGS = {
  slide_duration_seconds: 7,
  refresh_interval_seconds: 5,
  fade_duration_ms: 750,
  allow_shuffle: true,
  allow_fullscreen: true,
}

export default function AdminSettings() {
  const { token } = useAdmin()
  const [settings, setSettings] = useState(INITIAL_SETTINGS)
  const [error, setError] = useState('')
  const [notice, setNotice] = useState('')
  const [saving, setSaving] = useState(false)

  useEffect(() => {
    let active = true
    getAdminSettings(token)
      .then((result) => { if (active) setSettings(result) })
      .catch((requestError) => {
        if (active) setError(getApiErrorMessage(requestError, 'Could not load settings.'))
      })
    return () => { active = false }
  }, [token])

  function updateField(key, value) {
    setSettings((current) => ({ ...current, [key]: value }))
    setNotice('')
  }

  async function save(event) {
    event.preventDefault()
    setError('')
    setNotice('')
    setSaving(true)
    try {
      setSettings(await updateAdminSettings(token, {
        slide_duration_seconds: Number(settings.slide_duration_seconds),
        refresh_interval_seconds: Number(settings.refresh_interval_seconds),
        fade_duration_ms: Number(settings.fade_duration_ms),
        allow_shuffle: settings.allow_shuffle,
        allow_fullscreen: settings.allow_fullscreen,
      }))
      setNotice('Slideshow defaults saved.')
    } catch (requestError) {
      setError(getApiErrorMessage(requestError, 'Could not save slideshow settings.'))
    } finally {
      setSaving(false)
    }
  }

  return (
    <AdminLayout>
      <div className="admin-page-heading">
        <span className="eyebrow">Administration</span>
        <h1>Slideshow settings</h1>
        <p>Set defaults for displays. Visitors may override timing locally.</p>
      </div>
      <form className="admin-settings-form" onSubmit={save}>
        {error && <div className="alert-message" role="alert">{error}</div>}
        {notice && <div className="alert-message success" role="status">{notice}</div>}
        <label className="field-label" htmlFor="slide-duration">Default slide duration (seconds)</label>
        <input className="form-control-custom" id="slide-duration" max="30" min="3" onChange={(event) => updateField('slide_duration_seconds', event.target.value)} type="number" value={settings.slide_duration_seconds} />
        <label className="field-label" htmlFor="refresh-interval">Photo refresh interval (seconds)</label>
        <input className="form-control-custom" id="refresh-interval" max="300" min="5" onChange={(event) => updateField('refresh_interval_seconds', event.target.value)} type="number" value={settings.refresh_interval_seconds} />
        <label className="field-label" htmlFor="fade-duration">Default fade duration (milliseconds)</label>
        <select className="form-control-custom" id="fade-duration" onChange={(event) => updateField('fade_duration_ms', event.target.value)} value={settings.fade_duration_ms}>
          {[250, 500, 750, 1000, 1250, 1500, 1750, 2000].map((value) => <option key={value} value={value}>{value} ms</option>)}
        </select>
        <label className="admin-checkbox">
          <input checked={settings.allow_shuffle} onChange={(event) => updateField('allow_shuffle', event.target.checked)} type="checkbox" />
          Allow shuffle control
        </label>
        <label className="admin-checkbox">
          <input checked={settings.allow_fullscreen} onChange={(event) => updateField('allow_fullscreen', event.target.checked)} type="checkbox" />
          Allow fullscreen control
        </label>
        <button className="button-primary" disabled={saving} type="submit">{saving ? 'Saving…' : 'Save defaults'}</button>
      </form>
    </AdminLayout>
  )
}
