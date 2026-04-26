import { NavLink, Outlet } from 'react-router-dom'

export function AppLayout() {
  return (
    <div className="app-shell">
      <header className="app-header">
        <div className="brand-lockup">
          <span className="brand-mark" aria-hidden="true">
            <img src="/favicon.svg" alt="" />
          </span>
          <div className="brand-copy">
            <p className="eyebrow">Projeto Integrador de IA</p>
            <h1>Identificador de Abelhas</h1>
            <p className="app-subtitle">
              Classificação assistida de espécies do gênero <em>Augochloropsis</em>.
            </p>
          </div>
        </div>
        <nav className="app-nav" aria-label="Navegação principal">
          <NavLink
            to="/"
            className={({ isActive }) => (isActive ? 'nav-link nav-link-active' : 'nav-link')}
          >
            Classificar
          </NavLink>
          <NavLink
            to="/history"
            className={({ isActive }) => (isActive ? 'nav-link nav-link-active' : 'nav-link')}
          >
            Histórico
          </NavLink>
          <NavLink
            to="/species"
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
