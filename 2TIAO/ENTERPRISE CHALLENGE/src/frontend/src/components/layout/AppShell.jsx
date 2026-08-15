import { NavLink, Outlet } from 'react-router-dom';
import logoGenera from '../../assets/logo-genera.png';
import DisclaimerBar from './DisclaimerBar';

/**
 * Itens de navegação do dashboard. `end` garante que a rota raiz ("/")
 * só fique ativa na Home, e não em todas as subrotas.
 */
const NAV_ITEMS = [
  { to: '/', label: 'Início', end: true },
  { to: '/riscos', label: 'Riscos' },
  { to: '/ancestralidade', label: 'Ancestralidade' },
  { to: '/chat', label: 'Chat' },
  { to: '/historico', label: 'Histórico' },
];

function navLinkClasses({ isActive }) {
  const base =
    'block rounded-lg px-4 py-2 text-sm font-medium transition-colors focus:outline-none focus-visible:ring-2 focus-visible:ring-genera-magenta focus-visible:ring-offset-2';
  return isActive
    ? `${base} bg-genera-roxo text-white`
    : `${base} text-genera-roxo hover:bg-genera-roxo/10`;
}

/**
 * AppShell — layout base do dashboard (A1).
 * Cabeçalho com logo + navegação (tabs roláveis no mobile, sidebar no desktop
 * a partir de `md:`). O conteúdo de cada rota é renderizado no <Outlet/>.
 */
export default function AppShell() {
  return (
    <div className="flex min-h-screen flex-col bg-white font-sans text-genera-roxo">
      <header className="border-b border-gray-200 bg-white shadow-sm">
        <div className="mx-auto flex max-w-6xl items-center gap-3 px-4 py-3">
          <img
            src={logoGenera}
            alt="Genera"
            className="h-9 w-auto object-contain"
          />
          <span className="text-sm font-medium uppercase tracking-widest text-genera-roxo/60">
            Dashboard do Paciente
          </span>
        </div>

        {/* Navegação mobile: tabs horizontais roláveis (< md) */}
        <nav
          aria-label="Navegação principal"
          className="mx-auto flex max-w-6xl gap-1 overflow-x-auto px-2 pb-2 md:hidden"
        >
          {NAV_ITEMS.map((item) => (
            <NavLink
              key={item.to}
              to={item.to}
              end={item.end}
              className={navLinkClasses}
            >
              {item.label}
            </NavLink>
          ))}
        </nav>
      </header>

      <div className="mx-auto flex w-full max-w-6xl flex-1 flex-col md:flex-row">
        {/* Sidebar desktop (>= md) */}
        <aside className="hidden w-56 shrink-0 border-r border-gray-200 p-4 md:block">
          <nav aria-label="Navegação lateral" className="flex flex-col gap-1">
            {NAV_ITEMS.map((item) => (
              <NavLink
                key={item.to}
                to={item.to}
                end={item.end}
                className={navLinkClasses}
              >
                {item.label}
              </NavLink>
            ))}
          </nav>
        </aside>

        <main className="min-w-0 flex-1 p-4 md:p-6">
          <Outlet />
        </main>
      </div>

      <DisclaimerBar />
    </div>
  );
}
