import { FiLogOut } from 'react-icons/fi'
import { Link } from 'react-router-dom'
import { useVisitor } from '../hooks/useVisitor.js'

export default function Navbar() {
  const { visitor, clearSession } = useVisitor()

  return (
    <header className="site-header">
      <Link className="brand" to="/" aria-label="Memory Lane home">
        <span className="brand-mark" aria-hidden="true">
          M
        </span>
        <span className="brand-name">Memory Lane</span>
      </Link>
      <nav className="site-nav" aria-label="Main navigation">
        <Link to="/slideshow">Slideshow</Link>
        {visitor ? (
          <>
            <Link to="/dashboard">My photos</Link>
            <button className="nav-button" onClick={clearSession} type="button">
              <FiLogOut aria-hidden="true" /> Sign out
            </button>
          </>
        ) : (
          <Link className="nav-button" to="/returning">
            Access my photos
          </Link>
        )}
      </nav>
    </header>
  )
}
