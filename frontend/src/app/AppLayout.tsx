import { NavLink, Outlet, useNavigate } from 'react-router-dom'
import { useAuth } from '../features/auth/AuthContext'

export function AppLayout() {
  const { user, signOut } = useAuth()
  const navigate = useNavigate()

  async function handleSignOut() {
    await signOut()
    navigate('/login')
  }

  return (
    <div className="app-shell">
      <header className="app-header">
        <div className="brand-lockup">
          <span className="brand-mark">
            <img src="/logosolucoesmobile.png" alt="BeeAI" />
          </span>
          <div className="brand-copy">
            <p className="eyebrow">Projeto Integrador de IA</p>
            <h1>BeeAI</h1>
            <p className="app-subtitle">
              Identificação inteligente de espécies de abelhas
            </p>
          </div>
        </div>
        <nav className="app-nav" aria-label="Navegação principal">
          <NavLink
            to="/app"
            end
            className={({ isActive }) => (isActive ? 'nav-link nav-link-active' : 'nav-link')}
          >
            Classificar
          </NavLink>
          <NavLink
            to="/app/history"
            className={({ isActive }) => (isActive ? 'nav-link nav-link-active' : 'nav-link')}
          >
            Histórico
          </NavLink>
          <NavLink
            to="/app/species"
            className={({ isActive }) => (isActive ? 'nav-link nav-link-active' : 'nav-link')}
          >
            Espécies
          </NavLink>
          <div className="nav-user">
            <span className="nav-email">{user?.email}</span>
            <button className="btn-ghost" onClick={handleSignOut}>
              Sair
            </button>
          </div>
        </nav>
      </header>
      <main className="page-container">
        <Outlet />
      </main>
    </div>
  )
}
