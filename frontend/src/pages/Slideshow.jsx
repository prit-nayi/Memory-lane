import { useEffect, useState } from 'react'
import { FiArrowLeft, FiRefreshCw } from 'react-icons/fi'
import { Link } from 'react-router-dom'
import Loading from '../components/Loading.jsx'
import { getApiErrorMessage } from '../services/api.js'
import {
  getSlideshowPhotos,
  getSlideshowSettings,
} from '../services/slideshowService.js'

export default function Slideshow() {
  const [photos, setPhotos] = useState([])
  const [settings, setSettings] = useState({
    slide_duration_seconds: 7,
    refresh_interval_seconds: 30,
  })
  const [activeIndex, setActiveIndex] = useState(0)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')

  useEffect(() => {
    let active = true
    async function refresh() {
      try {
        const [latestPhotos, latestSettings] = await Promise.all([
          getSlideshowPhotos(),
          getSlideshowSettings(),
        ])
        if (active) {
          setPhotos(latestPhotos)
          setSettings(latestSettings)
          setError('')
        }
      } catch (requestError) {
        if (active) {
          setError(
            getApiErrorMessage(requestError, 'Could not load slideshow photos.'),
          )
        }
      } finally {
        if (active) {
          setLoading(false)
        }
      }
    }

    refresh()
    const refreshTimer = window.setInterval(
      refresh,
      settings.refresh_interval_seconds * 1000,
    )
    return () => {
      active = false
      window.clearInterval(refreshTimer)
    }
  }, [settings.refresh_interval_seconds])

  useEffect(() => {
    if (photos.length < 2) {
      return undefined
    }

    const slideTimer = window.setInterval(() => {
      setActiveIndex((index) => (index + 1) % photos.length)
    }, settings.slide_duration_seconds * 1000)
    return () => window.clearInterval(slideTimer)
  }, [photos.length, settings.slide_duration_seconds])

  if (loading) {
    return <Loading label="Loading the Memory Lane slideshow..." />
  }

  if (!photos.length) {
    return (
      <div className="slideshow-empty">
        <div>
          <span className="slideshow-kicker">Memory Lane</span>
          <h1>Every picture starts with a memory.</h1>
          <p>
            There are no photos yet. Share a moment and it will appear here as
            soon as the upload is complete.
          </p>
          {error && <div className="slideshow-error">{error}</div>}
          <Link className="slideshow-return" to="/">
            <FiArrowLeft aria-hidden="true" /> Back to Memory Lane
          </Link>
        </div>
      </div>
    )
  }

  const currentIndex = activeIndex % photos.length
  const currentPhoto = photos[currentIndex]
  return (
    <div className="slideshow-screen">
      <img
        alt={currentPhoto.original_filename}
        className="slideshow-image"
        key={currentPhoto.id}
        onError={() => {
          setError(`Could not load "${currentPhoto.original_filename}".`)
          setPhotos((current) =>
            current.filter((photo) => photo.id !== currentPhoto.id),
          )
        }}
        src={currentPhoto.image_url}
      />
      <div aria-hidden="true" className="slideshow-shade" />
      <div className="slideshow-brand">
        <span className="slideshow-brand-mark">M</span>
        <span>Memory Lane</span>
      </div>
      <div className="slideshow-caption">
        <span className="slideshow-kicker">A shared memory</span>
        <h1>{currentPhoto.original_filename}</h1>
      </div>
      <div aria-live="polite" className="slideshow-counter">
        {currentIndex + 1} <span>/</span> {photos.length}
      </div>
      {error && (
        <div className="slideshow-refresh-note" role="status">
          <FiRefreshCw aria-hidden="true" /> {error}
        </div>
      )}
      <Link aria-label="Exit slideshow" className="slideshow-exit" to="/">
        <FiArrowLeft aria-hidden="true" /> Exit slideshow
      </Link>
      </div>
  )
}
