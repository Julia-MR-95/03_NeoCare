import { BrowserRouter, Routes, Route, Navigate, useLocation } from 'react-router-dom'
import type { ReactNode } from 'react'
import { AuthProvider, useAuth } from './context/AuthContext'
import LoginPage from './components/pages/LoginPage'
import BoardPage from './components/pages/BoardPage'
import MyHoursPage from './components/pages/MyHoursPage'
import ReportPage from './components/pages/ReportPage'

// Ruta protegida: redirige a /login si no hay sesión recordando a dónde se iba
const PrivateRoute = ({ children }: { children: ReactNode }) => {
  const { user, loading } = useAuth()
  const location = useLocation()
  if (loading) return <div style={{ padding: '2rem' }}>Cargando...</div>
  if (user) return <>{children}</>
  const redirect = encodeURIComponent(location.pathname + location.search)
  return <Navigate to={`/login?redirect=${redirect}`} replace />
}

export default function App() {
  return (
    <BrowserRouter>
      <AuthProvider>
        <Routes>
          <Route path="/login" element={<LoginPage />} />
          <Route path="/" element={<PrivateRoute><BoardPage /></PrivateRoute>} />
          <Route path="/hours" element={<PrivateRoute><MyHoursPage /></PrivateRoute>} />
          <Route path="/report" element={<PrivateRoute><ReportPage /></PrivateRoute>} />
        </Routes>
      </AuthProvider>
    </BrowserRouter>
  )
}
