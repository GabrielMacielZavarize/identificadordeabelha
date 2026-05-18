import { Navigate, Outlet } from 'react-router-dom'
import { useAuth } from './AuthContext'
import { supabase } from '../../lib/supabase'

export function ProtectedRoute() {
  const { session, loading } = useAuth()

  // Supabase não configurado — acesso local liberado sem autenticação
  if (!supabase) return <Outlet />

  if (loading) {
    return (
      <div style={{ display: 'flex', justifyContent: 'center', padding: '4rem' }}>
        <span style={{ color: 'var(--muted)' }}>Carregando...</span>
      </div>
    )
  }

  if (!session) {
    return <Navigate to="/login" replace />
  }

  return <Outlet />
}
