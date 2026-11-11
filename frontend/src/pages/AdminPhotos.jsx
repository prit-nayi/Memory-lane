import { useEffect, useState } from 'react'
import { Link, useSearchParams } from 'react-router-dom'
import AdminLayout from '../components/AdminLayout.jsx'
import { useAdmin } from '../hooks/useAdmin.js'
import { getApiErrorMessage } from '../services/api.js'
import { deleteAdminPhoto, getAdminPhotos } from '../services/adminService.js'

export default function AdminPhotos() {
  const { token } = useAdmin()
  const [searchParams] = useSearchParams()
  const visitorId = searchParams.get('visitor_id')
  const [photos, setPhotos] = useState([])
  const [error, setError] = useState('')

  useEffect(() => {
    let active = true
    getAdminPhotos(token, visitorId)
      .then((result) => { if (active) setPhotos(result) })
      .catch((requestError) => {
        if (active) setError(getApiErrorMessage(requestError, 'Could not load photos.'))
      })
    return () => { active = false }
  }, [token, visitorId])

  async function removePhoto(photo) {
    if (!window.confirm(`Permanently remove "${photo.original_filename}"?`)) {
      return
    }
    try {
      await deleteAdminPhoto(token, photo.id)
      setPhotos((current) => current.filter((item) => item.id !== photo.id))
    } catch (requestError) {
      setError(getApiErrorMessage(requestError, 'Could not delete photo.'))
    }
  }

  return (
    <AdminLayout>
      <div className="admin-page-heading">
        <span className="eyebrow">Administration</span>
        <h1>Photos</h1>
        <p>Remove photos that should no longer remain in their owner's slideshow.</p>
        {visitorId && <Link className="button-text" to="/admin/photos">Show all visitors</Link>}
      </div>
      {error && <div className="alert-message" role="alert">{error}</div>}
      <div className="admin-table-wrap">
        <table className="admin-table">
          <thead><tr><th>Filename</th><th>Visitor</th><th>Type</th><th>Uploaded</th><th /></tr></thead>
          <tbody>
            {photos.map((photo) => (
              <tr key={photo.id}>
                <td>{photo.original_filename}</td>
                <td>{photo.visitor_name}</td>
                <td>{photo.content_type}</td>
                <td>{new Date(photo.created_at).toLocaleDateString()}</td>
                <td><button className="button-secondary admin-action danger" onClick={() => removePhoto(photo)} type="button">Delete</button></td>
              </tr>
            ))}
            {!photos.length && <tr><td colSpan="5">No photos uploaded yet.</td></tr>}
          </tbody>
        </table>
      </div>
    </AdminLayout>
  )
}
