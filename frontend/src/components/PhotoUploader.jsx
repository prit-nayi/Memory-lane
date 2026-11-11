import { useEffect, useRef, useState } from 'react'
import { FiImage, FiPlus, FiUpload, FiX } from 'react-icons/fi'

const ACCEPTED_TYPES = new Set(['image/jpeg', 'image/png', 'image/webp'])

export default function PhotoUploader({
  onUpload,
  uploading,
  progress,
  error,
  success,
}) {
  const inputRef = useRef(null)
  const previewUrls = useRef(new Set())
  const [selected, setSelected] = useState([])
  const [selectionError, setSelectionError] = useState('')

  useEffect(() => {
    const urls = previewUrls.current
    return () => urls.forEach((url) => URL.revokeObjectURL(url))
  }, [])

  function addFiles(fileList) {
    const chosenFiles = Array.from(fileList)
    const supportedFiles = chosenFiles.filter((file) =>
      ACCEPTED_TYPES.has(file.type),
    )
    const additions = supportedFiles
      .map((file) => ({
        id: `${file.name}-${file.size}-${file.lastModified}-${Math.random()}`,
        file,
        preview: URL.createObjectURL(file),
      }))

    additions.forEach((item) => previewUrls.current.add(item.preview))
    if (additions.length) {
      setSelected((current) => [...current, ...additions])
    }
    setSelectionError(
      supportedFiles.length < chosenFiles.length
        ? 'Some files were skipped. Choose JPEG, PNG, or WebP images.'
        : '',
    )
    if (inputRef.current) {
      inputRef.current.value = ''
    }
  }

  function removeFile(id) {
    const removed = selected.find((item) => item.id === id)
    if (removed) {
      URL.revokeObjectURL(removed.preview)
      previewUrls.current.delete(removed.preview)
    }
    setSelected((current) => current.filter((item) => item.id !== id))
  }

  async function submit(event) {
    event.preventDefault()
    if (!selected.length || uploading) {
      return
    }
    const completed = await onUpload(selected.map((item) => item.file))
    if (completed) {
      selected.forEach((item) => {
        URL.revokeObjectURL(item.preview)
        previewUrls.current.delete(item.preview)
      })
      setSelected([])
    }
  }

  return (
    <form onSubmit={submit}>
      {(error || selectionError) && (
        <div className="alert-message" role="alert">
          {error || selectionError}
        </div>
      )}
      {success && (
        <div className="alert-message success" role="status">
          {success}
        </div>
      )}
      <div className="dropzone">
        <span className="dropzone-icon">
          <FiImage aria-hidden="true" />
        </span>
        <strong>Choose moments to share</strong>
        <span>JPEG, PNG, or WebP images</span>
        <input
          ref={inputRef}
          className="file-input"
          id="photo-files"
          accept="image/jpeg,image/png,image/webp"
          multiple
          onChange={(event) => addFiles(event.target.files)}
          type="file"
        />
        <label className="button-secondary" htmlFor="photo-files">
          <FiPlus aria-hidden="true" /> Browse photos
        </label>
      </div>

      {selected.length > 0 && (
        <>
          <div className="selected-heading">
            <span>Selected photos</span>
            <span>{selected.length}</span>
          </div>
          <div className="preview-grid">
            {selected.map((item) => (
              <div className="preview-card" key={item.id}>
                <img src={item.preview} alt={`Preview of ${item.file.name}`} />
                <span className="preview-name" title={item.file.name}>
                  {item.file.name}
                </span>
                <button
                  aria-label={`Remove ${item.file.name}`}
                  className="preview-remove"
                  disabled={uploading}
                  onClick={() => removeFile(item.id)}
                  type="button"
                >
                  <FiX aria-hidden="true" />
                </button>
              </div>
            ))}
          </div>
          {uploading && (
            <div aria-live="polite">
              <div
                className="progress-track"
                role="progressbar"
                aria-label="Upload progress"
                aria-valuenow={progress}
                aria-valuemin="0"
                aria-valuemax="100"
              >
                <div
                  className="progress-fill"
                  style={{ width: `${progress}%` }}
                />
              </div>
              <div className="progress-label">Uploading… {progress}%</div>
            </div>
          )}
          <button
            className="button-primary form-submit"
            disabled={uploading}
            style={{ marginTop: 18 }}
            type="submit"
          >
            <FiUpload aria-hidden="true" />
            {uploading ? 'Uploading photos…' : 'Upload photos'}
          </button>
        </>
      )}
    </form>
  )
}
