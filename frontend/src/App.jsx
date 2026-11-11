import { BrowserRouter } from 'react-router-dom'
import { VisitorProvider } from './context/VisitorContext.jsx'
import AppRoutes from './routes/AppRoutes.jsx'
import './App.css'

function App() {
  return (
    <BrowserRouter>
      <VisitorProvider>
        <AppRoutes />
      </VisitorProvider>
    </BrowserRouter>
  )
}

export default App
