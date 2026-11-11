import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import AdminLayout from '../components/AdminLayout.jsx'
import { useAdmin } from '../hooks/useAdmin.js'
import { getApiErrorMessage } from '../services/api.js'
import { getAdminDashboard } from '../services/adminService.js'

export default function AdminDashboard() {
  const { token } = useAdmin()
  const [dashboard, setDashboard] = useState(null)
  const [error, setError] = useState('')

  useEffect(() => {
    let active = true
    getAdminDashboard(token)
      .then((result) => {
        if (active) setDashboard(result)
      })
      .catch((requestError) => {
        if (active) {
          setError(getApiErrorMessage(requestError, 'Could not load dashboard.'))
        }
      })
    return () => { active = false }
  }, [token])

  return (
    <AdminLayout>
      <div className="admin-page-heading">
        <span className="eyebrow">Administration</span>
        <h1>Overview</h1>
        <p>Manage the people and photos in Memory Lane.</p>
      </div>
      {error && <div className="alert-message" role="alert">{error}</div>}
      {dashboard && (
        <div className="admin-stats">
          <article><span>Total visitors</span><strong>{dashboard.total_visitors}</strong></article>
          <article><span>Active visitors</span><strong>{dashboard.active_visitors}</strong></article>
          <article><span>Uploaded photos</span><strong>{dashboard.total_photos}</strong></article>
        </div>
      )}
      <div className="admin-quick-links">
        <Link className="button-primary" to="/admin/visitors">Manage visitors</Link>
        <Link className="button-secondary" to="/admin/photos">Manage photos</Link>
        <Link className="button-secondary" to="/admin/settings">Slideshow settings</Link>
      </div>
    </AdminLayout>
  )
}
