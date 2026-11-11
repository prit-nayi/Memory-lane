import { useState } from 'react'
import { FiArrowLeft, FiCheckCircle, FiMonitor } from 'react-icons/fi'
import { Link } from 'react-router-dom'
import PhotoUploader from '../components/PhotoUploader.jsx'
import { useVisitor } from '../hooks/useVisitor.js'
import { getApiErrorMessage } from '../services/api.js'
import { uploadPhotos } from '../services/photoService.js'

export default function UploadPhotos() {
  const { accessCode } = useVisitor()
  const [uploading, setUploading] = useState(false)
  const [progress, setProgress] = useState(0)
  const [error, setError] = useState('')
  const [success, setSuccess] = useState('')

  async function submitPhotos(files) {
    setError('')
    setSuccess('')
    setProgress(0)
    setUploading(true)
    try {
      const uploaded = await uploadPhotos(accessCode, files, setProgress)
      setSuccess(
        `${uploaded.length} ${uploaded.length === 1 ? 'photo is' : 'photos are'} now on the slideshow.`,
      )
      setProgress(100)
      return true
    } catch (requestError) {
      setError(
        getApiErrorMessage(requestError, 'Could not upload your selected photos.'),
      )
      return false
    } finally {
      setUploading(false)
    }
  }

  return (
    <div className="page-container">
      <Link className="button-text" to="/dashboard">
        <FiArrowLeft aria-hidden="true" /> Back to your photos
      </Link>
      <div className="page-heading" style={{ marginTop: 16 }}>
        <span className="eyebrow">Share a moment</span>
        <h1>Add to your Memory Lane.</h1>
        <p>
          Choose the photos you would like to share. Valid images are added
          directly to your personal slideshow as soon as the upload finishes.
        </p>
      </div>

      <div className="upload-layout">
        <div className="content-card" style={{ padding: 22 }}>
          <PhotoUploader
            error={error}
            onUpload={submitPhotos}
            progress={progress}
            success={success}
            uploading={uploading}
          />
          {success && (
            <Link className="button-text" style={{ marginTop: 12 }} to="/dashboard">
              View your collection <FiArrowLeft style={{ transform: 'rotate(180deg)' }} />
            </Link>
          )}
        </div>

        <aside className="upload-side-card">
          <h2>A few helpful notes</h2>
          <p>Your photos are connected to your visitor profile and shared on the slideshow.</p>
          <ul>
            <li>JPEG, PNG, and WebP images are supported.</li>
            <li>Image format and size are checked during upload.</li>
            <li>Valid uploads appear on the slideshow immediately.</li>
          </ul>
          <div className="alert-message success" style={{ margin: '18px 0 0' }}>
            <FiMonitor aria-hidden="true" /> Your photos are shared directly;
            there is no approval queue.
          </div>
          <div className="progress-label" style={{ marginTop: 15 }}>
            <FiCheckCircle aria-hidden="true" /> Your files are checked before
            they are saved.
          </div>
        </aside>
      </div>
    </div>
  )
}
