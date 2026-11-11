import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import AdminLayout from '../components/AdminLayout.jsx'
import { useAdmin } from '../hooks/useAdmin.js'
import { getApiErrorMessage } from '../services/api.js'
import { getAdminVisitors, updateAdminVisitor } from '../services/adminService.js'

export default function AdminVisitors() {
  const { token } = useAdmin()
  const [visitors, setVisitors] = useState([])
  const [error, setError] = useState('')
  const [updatingId, setUpdatingId] = useState('')

  useEffect(() => {
    let active = true
    getAdminVisitors(token)
      .then((result) => { if (active) setVisitors(result) })
      .catch((requestError) => {
        if (active) setError(getApiErrorMessage(requestError, 'Could not load visitors.'))
      })
    return () => { active = false }
  }, [token])

  async function toggleVisitor(visitor) {
    setUpdatingId(visitor.id)
    try {
      const updated = await updateAdminVisitor(token, visitor.id, !visitor.is_active)
      setVisitors((current) =>
        current.map((item) => item.id === updated.id ? updated : item),
      )
      setError('')
    } catch (requestError) {
      setError(getApiErrorMessage(requestError, 'Could not update visitor.'))
    } finally {
      setUpdatingId('')
    }
  }

  return (
    <AdminLayout>
      <div className="admin-page-heading">
        <span className="eyebrow">Administration</span>
        <h1>Visitors</h1>
        <p>Disable access temporarily without deleting visitor photos.</p>
      </div>
      {error && <div className="alert-message" role="alert">{error}</div>}
      <div className="admin-table-wrap">
        <table className="admin-table">
          <thead><tr><th>Name</th><th>Photos</th><th>Joined</th><th>Access</th><th>Manage</th><th /></tr></thead>
          <tbody>
            {visitors.map((visitor) => (
              <tr key={visitor.id}>
                <td>{visitor.name}</td>
                <td>{visitor.photo_count}</td>
                <td>{new Date(visitor.created_at).toLocaleDateString()}</td>
                <td><span className={`admin-state ${visitor.is_active ? 'enabled' : 'disabled'}`}>{visitor.is_active ? 'Active' : 'Disabled'}</span></td>
                <td><Link to={`/admin/photos?visitor_id=${visitor.id}`}>View photos</Link></td>
                <td>
                  <button
                    className="button-secondary admin-action"
                    disabled={updatingId === visitor.id}
                    onClick={() => toggleVisitor(visitor)}
                    type="button"
                  >
                    {updatingId === visitor.id ? 'Saving…' : visitor.is_active ? 'Disable' : 'Reactivate'}
                  </button>
                </td>
              </tr>
            ))}
            {!visitors.length && <tr><td colSpan="6">No visitors registered yet.</td></tr>}
          </tbody>
        </table>
      </div>
    </AdminLayout>
  )
}
