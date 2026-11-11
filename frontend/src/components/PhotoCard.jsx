import { FiFile, FiTrash2 } from 'react-icons/fi'

function formatDate(value) {
  return new Intl.DateTimeFormat(undefined, {
    month: 'short',
    day: 'numeric',
    year: 'numeric',
  }).format(new Date(value))
}

export default function PhotoCard({ photo, onDelete, deleting = false }) {
  return (
    <article className="photo-card">
      <div className="photo-card-top">
        <span className="photo-file-icon">
          <FiFile aria-hidden="true" />
        </span>
        <span className="status-pill live">On slideshow</span>
      </div>
      <h3 className="photo-filename" title={photo.original_filename}>
        {photo.original_filename}
      </h3>
      <div className="photo-date">
        Uploaded {formatDate(photo.created_at)}
      </div>
      <div className="photo-card-bottom">
        <span>{Math.max(1, Math.round(photo.file_size / 1024))} KB</span>
        {onDelete ? (
          <button
            className="button-danger"
            disabled={deleting}
            onClick={() => onDelete(photo)}
            type="button"
          >
            <FiTrash2 aria-hidden="true" />
            {deleting ? 'Removing…' : 'Remove'}
          </button>
        ) : null}
      </div>
    </article>
  )
}
