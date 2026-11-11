export default function Loading({ label = 'Loading your account...' }) {
  return (
    <div className="loading-state" role="status" aria-live="polite">
      <span className="spinner-border" aria-hidden="true" />
      <span>{label}</span>
    </div>
  )
}
