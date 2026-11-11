import { FiLogOut, FiSettings, FiUsers, FiImage, FiGrid } from 'react-icons/fi'
import { NavLink, useNavigate } from 'react-router-dom'
import { useAdmin } from '../hooks/useAdmin.js'

export default function AdminSidebar() {
  const { logout } = useAdmin()
  const navigate = useNavigate()

  function signOut() {
    logout()
    navigate('/admin/login', { replace: true })
  }

  return (
    <aside className="admin-sidebar">
      <div className="admin-sidebar-title">Memory Lane Admin</div>
      <nav aria-label="Admin navigation">
        <NavLink end to="/admin">
          <FiGrid aria-hidden="true" /> Overview
        </NavLink>
        <NavLink to="/admin/visitors">
          <FiUsers aria-hidden="true" /> Visitors
        </NavLink>
        <NavLink to="/admin/photos">
          <FiImage aria-hidden="true" /> Photos
        </NavLink>
        <NavLink to="/admin/settings">
          <FiSettings aria-hidden="true" /> Slideshow settings
        </NavLink>
      </nav>
      <button className="admin-logout" onClick={signOut} type="button">
        <FiLogOut aria-hidden="true" /> Sign out
      </button>
    </aside>
  )
}
