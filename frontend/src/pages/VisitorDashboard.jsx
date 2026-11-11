import { useEffect, useState } from 'react'
import { FiArrowRight, FiImage, FiPlus } from 'react-icons/fi'
import { Link } from 'react-router-dom'
import { useVisitor } from '../hooks/useVisitor.js'
import Loading from '../components/Loading.jsx'
import PhotoCard from '../components/PhotoCard.jsx'
import { getApiErrorMessage } from '../services/api.js'
import { deletePhoto, getMyPhotos } from '../services/photoService.js'

export default function VisitorDashboard() {
  const { visitor, accessCode } = useVisitor()
  const [photos, setPhotos] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')
  const [deletingId, setDeletingId] = useState('')

  useEffect(() => {
    let active = true
    getMyPhotos(accessCode)
      .then((result) => {
        if (active) {
          setPhotos(result)
        }
      })
      .catch((requestError) => {
        if (active) {
          setError(getApiErrorMessage(requestError, 'Could not load your photos.'))
        }
      })
      .finally(() => {
        if (active) {
          setLoading(false)
        }
      })
    return () => {
      active = false
    }
  }, [accessCode])

  async function removePhoto(photo) {
    if (!window.confirm(`Remove "${photo.original_filename}" from your photos?`)) {
      return
    }
    setDeletingId(photo.id)
    setError('')
    try {
      await deletePhoto(accessCode, photo.id)
      setPhotos((current) => current.filter((item) => item.id !== photo.id))
    } catch (requestError) {
      setError(getApiErrorMessage(requestError, 'Could not remove this photo.'))
    } finally {
      setDeletingId('')
    }
  }

  return (
    <div className="page-container">
      <div className="dashboard-top">
        <div>
          <span className="eyebrow">Your Memory Lane</span>
          <h1 className="visitor-greeting">
            Welcome back, <span>{visitor.name}</span>
          </h1>
          <div className="dashboard-meta">
            Your shared moments, all in one place.
          </div>
        </div>
        <Link className="button-primary" to="/upload">
          <FiPlus aria-hidden="true" /> Add photos
        </Link>
      </div>

      <div className="stats-row" aria-label="Photo summary">
        <div className="stat-card">
          <span className="stat-label">Photos shared</span>
          <span className="stat-value">{photos.length}</span>
        </div>
        <div className="stat-card">
          <span className="stat-label">Photos on slideshow</span>
          <span className="stat-value">{photos.length}</span>
        </div>
      </div>

      <div className="section-title-row">
        <h2>Your photos</h2>
        {photos.length > 0 && (
          <Link className="button-text" to="/upload">
            Share another <FiArrowRight aria-hidden="true" />
          </Link>
        )}
      </div>

      {error && (
        <div className="alert-message" role="alert">
          {error}
        </div>
      )}

      {loading ? (
        <Loading label="Gathering your photos..." />
      ) : photos.length === 0 ? (
        <div className="empty-state">
          <span className="empty-icon">
            <FiImage aria-hidden="true" />
          </span>
          <h3>Your collection starts here</h3>
          <p>Share a photo and add a new memory to Memory Lane.</p>
          <Link className="button-primary" to="/upload">
            Upload your first photos <FiArrowRight aria-hidden="true" />
          </Link>
        </div>
      ) : (
        <div className="photo-grid">
          {photos.map((photo) => (
            <PhotoCard
              deleting={deletingId === photo.id}
              key={photo.id}
              onDelete={removePhoto}
              photo={photo}
            />
          ))}
        </div>
      )}
    </div>
  )
}
