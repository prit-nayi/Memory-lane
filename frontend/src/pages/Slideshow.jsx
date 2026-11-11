import { useCallback, useEffect, useState } from 'react'
import {
  FiArrowLeft,
  FiChevronLeft,
  FiChevronRight,
  FiMaximize,
  FiMinimize,
  FiPause,
  FiPlay,
  FiRefreshCw,
  FiShuffle,
  FiSliders,
} from 'react-icons/fi'
import { Link } from 'react-router-dom'
import Loading from '../components/Loading.jsx'
import useSlideshowSocket from '../hooks/useSlideshowSocket.js'
import { useVisitor } from '../hooks/useVisitor.js'
import { getApiErrorMessage } from '../services/api.js'
import {
  getSlideshowPhotos,
  getSlideshowPhotoImage,
  getSlideshowSettings,
} from '../services/slideshowService.js'

const PREFERENCES_KEY = 'memory-lane-slideshow-preferences'
const DEFAULT_PREFERENCES = {
  slideDurationSeconds: 7,
  fadeDurationMs: 750,
}

function loadPreferences() {
  try {
    const raw = localStorage.getItem(PREFERENCES_KEY)
    if (!raw) return null
    const stored = JSON.parse(raw)
    return {
      slideDurationSeconds:
        Number.isInteger(stored.slideDurationSeconds) &&
        stored.slideDurationSeconds >= 3 &&
        stored.slideDurationSeconds <= 30
          ? stored.slideDurationSeconds
          : null,
      fadeDurationMs:
        Number.isInteger(stored.fadeDurationMs) &&
        stored.fadeDurationMs >= 250 &&
        stored.fadeDurationMs <= 2000 &&
        (stored.fadeDurationMs - 250) % 250 === 0
          ? stored.fadeDurationMs
          : null,
    }
  } catch {
    return null
  }
}

function uniquePhotos(photos) {
  return [...new Map(photos.map((photo) => [photo.id, photo])).values()]
}

export default function Slideshow() {
  const { accessCode, clearSession } = useVisitor()
  const [photos, setPhotos] = useState([])
  const [imageSource, setImageSource] = useState(null)
  const [settings, setSettings] = useState({
    slide_duration_seconds: DEFAULT_PREFERENCES.slideDurationSeconds,
    refresh_interval_seconds: 5,
    fade_duration_ms: DEFAULT_PREFERENCES.fadeDurationMs,
    allow_shuffle: true,
    allow_fullscreen: true,
  })
  const [preferences, setPreferences] = useState(loadPreferences)
  const [activeIndex, setActiveIndex] = useState(0)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')
  const [isPlaying, setIsPlaying] = useState(true)
  const [isShuffled, setIsShuffled] = useState(false)
  const [controlsVisible, setControlsVisible] = useState(true)
  const [isFullscreen, setIsFullscreen] = useState(false)
  const [preferenceError, setPreferenceError] = useState('')

  const refreshPhotos = useCallback(async () => {
    try {
      const latestPhotos = uniquePhotos(await getSlideshowPhotos(accessCode))
      setPhotos(latestPhotos)
      setActiveIndex((index) => Math.min(index, Math.max(0, latestPhotos.length - 1)))
      setError('')
    } catch (requestError) {
      if (requestError.response?.status === 401) {
        setPhotos([])
        setImageSource(null)
        clearSession()
      }
      setError(
        getApiErrorMessage(requestError, 'Could not load slideshow photos.'),
      )
    }
  }, [accessCode, clearSession])

  useEffect(() => {
    let active = true
    async function refresh() {
      try {
        const [latestPhotos, latestSettings] = await Promise.all([
          getSlideshowPhotos(accessCode),
          getSlideshowSettings(),
        ])
        if (active) {
          const unique = uniquePhotos(latestPhotos)
          setPhotos(unique)
          setActiveIndex((index) => Math.min(index, Math.max(0, unique.length - 1)))
          setSettings(latestSettings)
          setError('')
        }
      } catch (requestError) {
        if (active) {
          if (requestError.response?.status === 401) {
            setPhotos([])
            setImageSource(null)
            clearSession()
          }
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
  }, [accessCode, clearSession, settings.refresh_interval_seconds])

  const connectionState = useSlideshowSocket(refreshPhotos)
  const currentPhoto = photos.length
    ? photos[activeIndex % photos.length]
    : null
  const currentPhotoId = currentPhoto?.id
  const currentPhotoImageUrl = currentPhoto?.image_url
  const currentPhotoFilename = currentPhoto?.original_filename
  const slideDurationSeconds =
    preferences?.slideDurationSeconds ?? settings.slide_duration_seconds
  const fadeDurationMs =
    preferences?.fadeDurationMs ?? settings.fade_duration_ms

  useEffect(() => {
    let active = true
    let objectUrl

    if (!currentPhotoId || !currentPhotoImageUrl) {
      return () => {
        active = false
      }
    }

    getSlideshowPhotoImage(accessCode, currentPhotoImageUrl)
      .then((imageBlob) => {
        objectUrl = URL.createObjectURL(imageBlob)
        if (active) {
          setImageSource({ photoId: currentPhotoId, url: objectUrl })
        } else {
          URL.revokeObjectURL(objectUrl)
        }
      })
      .catch((requestError) => {
        if (active) {
          if (requestError.response?.status === 401) {
            setPhotos([])
            setImageSource(null)
            clearSession()
          }
          setError(
            getApiErrorMessage(
              requestError,
              `Could not load "${currentPhotoFilename}".`,
            ),
          )
        }
      })

    return () => {
      active = false
      if (objectUrl) {
        URL.revokeObjectURL(objectUrl)
      }
    }
  }, [
    accessCode,
    clearSession,
    currentPhotoFilename,
    currentPhotoId,
    currentPhotoImageUrl,
  ])

  useEffect(() => {
    if (!isPlaying || photos.length < 2) {
      return undefined
    }

    const slideTimer = window.setInterval(() => {
      setActiveIndex((index) => {
        if (isShuffled && settings.allow_shuffle) {
          const randomIndex = Math.floor(Math.random() * (photos.length - 1))
          return randomIndex >= index ? randomIndex + 1 : randomIndex
        }
        return (index + 1) % photos.length
      })
    }, slideDurationSeconds * 1000)
    return () => window.clearInterval(slideTimer)
  }, [
    isPlaying,
    isShuffled,
    photos.length,
    settings.allow_shuffle,
    slideDurationSeconds,
  ])

  useEffect(() => {
    const syncFullscreen = () => setIsFullscreen(Boolean(document.fullscreenElement))
    document.addEventListener('fullscreenchange', syncFullscreen)
    return () => document.removeEventListener('fullscreenchange', syncFullscreen)
  }, [])

  function moveSlide(direction) {
    setActiveIndex((index) => (index + direction + photos.length) % photos.length)
  }

  function updatePreferences(changes) {
    const updatedPreferences = {
      slideDurationSeconds,
      fadeDurationMs,
      ...changes,
    }
    setPreferences(updatedPreferences)
    try {
      localStorage.setItem(
        PREFERENCES_KEY,
        JSON.stringify(updatedPreferences),
      )
      setPreferenceError('')
    } catch {
      setPreferenceError(
        'Playback preferences could not be saved in this browser.',
      )
    }
  }

  async function toggleFullscreen() {
    try {
      if (document.fullscreenElement) {
        await document.exitFullscreen()
      } else {
        await document.documentElement.requestFullscreen()
      }
    } catch {
      setError('Fullscreen mode is not available in this browser.')
    }
  }

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
  return (
    <div className="slideshow-screen">
      <img
        alt={currentPhoto.original_filename}
        className="slideshow-image"
        key={`${currentPhoto.id}-${fadeDurationMs}`}
        onError={() => {
          setError(`Could not load "${currentPhoto.original_filename}".`)
          setPhotos((current) =>
            current.filter((photo) => photo.id !== currentPhoto.id),
          )
        }}
        src={
          imageSource?.photoId === currentPhoto.id
            ? imageSource.url
            : undefined
        }
        style={{ '--transition-duration': `${fadeDurationMs}ms` }}
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
      <div
        aria-label={`Slideshow connection ${connectionState}`}
        className={`slideshow-connection ${connectionState}`}
        title={`Live updates ${connectionState}`}
      >
        {connectionState === 'connected'
          ? 'Live updates on'
          : 'Reconnecting live updates'}
      </div>
      {controlsVisible ? (
        <section aria-label="Slideshow controls" className="slideshow-controls">
          <div className="slideshow-control-actions">
            <button
              aria-label="Previous photo"
              disabled={photos.length < 2}
              onClick={() => moveSlide(-1)}
              type="button"
            >
              <FiChevronLeft aria-hidden="true" />
            </button>
            <button
              aria-label={isPlaying ? 'Pause slideshow' : 'Play slideshow'}
              onClick={() => setIsPlaying((playing) => !playing)}
              type="button"
            >
              {isPlaying ? <FiPause aria-hidden="true" /> : <FiPlay aria-hidden="true" />}
            </button>
            <button
              aria-label="Next photo"
              disabled={photos.length < 2}
              onClick={() => moveSlide(1)}
              type="button"
            >
              <FiChevronRight aria-hidden="true" />
            </button>
            {settings.allow_shuffle && (
              <button
                aria-label={isShuffled ? 'Disable shuffle' : 'Enable shuffle'}
                aria-pressed={isShuffled}
                className={isShuffled ? 'active' : ''}
                onClick={() => setIsShuffled((shuffled) => !shuffled)}
                type="button"
              >
                <FiShuffle aria-hidden="true" />
              </button>
            )}
            {settings.allow_fullscreen && (
              <button
                aria-label={isFullscreen ? 'Exit fullscreen' : 'Enter fullscreen'}
                onClick={toggleFullscreen}
                type="button"
              >
                {isFullscreen ? <FiMinimize aria-hidden="true" /> : <FiMaximize aria-hidden="true" />}
              </button>
            )}
          </div>
          <label className="slideshow-slider">
            <span>
              Slide duration <output>{slideDurationSeconds}s</output>
            </span>
            <input
              max="30"
              min="3"
              onChange={(event) =>
                updatePreferences({
                  slideDurationSeconds: Number(event.target.value),
                })
              }
              type="range"
              value={slideDurationSeconds}
            />
          </label>
          <label className="slideshow-slider">
            <span>
              Fade speed{' '}
              <output>{(fadeDurationMs / 1000).toFixed(2)}s</output>
            </span>
            <input
              max="2000"
              min="250"
              onChange={(event) =>
                updatePreferences({
                  fadeDurationMs: Number(event.target.value),
                })
              }
              step="250"
              type="range"
              value={fadeDurationMs}
            />
          </label>
          {preferenceError && (
            <p className="slideshow-preference-error" role="alert">
              {preferenceError}
            </p>
          )}
          <button
            aria-label="Hide slideshow controls"
            className="slideshow-controls-hide"
            onClick={() => setControlsVisible(false)}
            type="button"
          >
            <FiSliders aria-hidden="true" /> Hide
          </button>
        </section>
      ) : (
        <button
          aria-label="Show slideshow controls"
          className="slideshow-controls-show"
          onClick={() => setControlsVisible(true)}
          type="button"
        >
          <FiSliders aria-hidden="true" />
        </button>
      )}
      <Link aria-label="Exit slideshow" className="slideshow-exit" to="/">
        <FiArrowLeft aria-hidden="true" /> Exit slideshow
      </Link>
    </div>
  )
}
