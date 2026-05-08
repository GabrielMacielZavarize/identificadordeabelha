import { NavLink, Outlet } from 'react-router-dom'

export function AppLayout() {
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
        </nav>
      </header>
      <main className="page-container">
        <Outlet />
      </main>
    </div>
  )
}
