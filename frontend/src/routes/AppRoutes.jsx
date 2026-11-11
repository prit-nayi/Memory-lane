import { Navigate, Route, Routes } from 'react-router-dom'
import Footer from '../components/Footer.jsx'
import Loading from '../components/Loading.jsx'
import Navbar from '../components/Navbar.jsx'
import { useVisitor } from '../hooks/useVisitor.js'
import Home from '../pages/Home.jsx'
import Register from '../pages/Register.jsx'
import ReturningVisitor from '../pages/ReturningVisitor.jsx'
import Slideshow from '../pages/Slideshow.jsx'
import UploadPhotos from '../pages/UploadPhotos.jsx'
import VisitorDashboard from '../pages/VisitorDashboard.jsx'

function ProtectedRoute({ children }) {
  const { visitor, loading } = useVisitor()
  if (loading) {
    return <Loading />
  }
  return visitor ? children : <Navigate replace to="/returning" />
}

export default function AppRoutes() {
  const { sessionError, loading } = useVisitor()
  return (
    <div className="site-shell">
      <Navbar />
      <main className="site-main">
        {sessionError && !loading && (
          <div className="alert-message" role="alert" style={{ width: 'min(1060px, calc(100% - 48px))', margin: '18px auto 0' }}>
            {sessionError}
          </div>
        )}
        <Routes>
          <Route element={<Home />} path="/" />
          <Route element={<Register />} path="/register" />
          <Route element={<ReturningVisitor />} path="/returning" />
          <Route
            element={
              <ProtectedRoute>
                <VisitorDashboard />
              </ProtectedRoute>
            }
            path="/dashboard"
          />
          <Route
            element={
              <ProtectedRoute>
                <UploadPhotos />
              </ProtectedRoute>
            }
            path="/upload"
          />
          <Route element={<Slideshow />} path="/slideshow" />
          <Route element={<Navigate replace to="/" />} path="*" />
        </Routes>
      </main>
      <Footer />
    </div>
  )
}
