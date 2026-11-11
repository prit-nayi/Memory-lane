import { BrowserRouter } from 'react-router-dom'
import { VisitorProvider } from './context/VisitorContext.jsx'
import { AdminProvider } from './context/AdminContext.jsx'
import AppRoutes from './routes/AppRoutes.jsx'
import './App.css'

function App() {
  return (
    <BrowserRouter>
      <AdminProvider>
        <VisitorProvider>
          <AppRoutes />
        </VisitorProvider>
      </AdminProvider>
    </BrowserRouter>
  )
}

export default App
