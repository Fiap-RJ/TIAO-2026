import { createBrowserRouter, RouterProvider } from 'react-router-dom';
import AppShell from './components/layout/AppShell';
import HomePage from './pages/HomePage';
import RiscosPage from './pages/RiscosPage';
import AncestralidadePage from './pages/AncestralidadePage';
import ChatPage from './pages/ChatPage';
import HistoricoPage from './pages/HistoricoPage';

const router = createBrowserRouter([
  {
    path: '/',
    element: <AppShell />,
    children: [
      { index: true, element: <HomePage /> },
      { path: 'riscos', element: <RiscosPage /> },
      { path: 'ancestralidade', element: <AncestralidadePage /> },
      { path: 'chat', element: <ChatPage /> },
      { path: 'historico', element: <HistoricoPage /> },
    ],
  },
]);

export default function App() {
  return <RouterProvider router={router} />;
}
