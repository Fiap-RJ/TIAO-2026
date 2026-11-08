import type { ReactNode } from 'react'
import { BrowserRouter, Navigate, Route, Routes, useParams } from 'react-router-dom'
import { AuthProvider } from './auth/AuthContext'
import { rotaInicial, useAuth } from './auth/useAuth'
import { Layout } from './components/Layout'
import { LoginPage } from './pages/LoginPage'
import { PacientePage } from './pages/PacientePage'
import { PacientesPage } from './pages/PacientesPage'

function Protegida({ children, apenasMedico = false }: { children: ReactNode; apenasMedico?: boolean }) {
  const { usuario } = useAuth()
  if (!usuario) return <Navigate to="/login" replace />
  if (apenasMedico && usuario.perfil !== 'medico') return <Navigate to={rotaInicial(usuario)} replace />
  return <Layout>{children}</Layout>
}

/** Paciente só acessa o próprio painel. */
function PainelPaciente() {
  const { usuario } = useAuth()
  const { id } = useParams()
  if (usuario?.perfil === 'paciente' && usuario.paciente_id !== id) {
    return <Navigate to={rotaInicial(usuario)} replace />
  }
  return <PacientePage key={id} />
}

function Inicio() {
  const { usuario } = useAuth()
  return <Navigate to={usuario ? rotaInicial(usuario) : '/login'} replace />
}

export default function App() {
  return (
    <BrowserRouter>
      <AuthProvider>
        <Routes>
          <Route path="/login" element={<LoginPage />} />
          <Route
            path="/pacientes"
            element={
              <Protegida apenasMedico>
                <PacientesPage />
              </Protegida>
            }
          />
          <Route
            path="/pacientes/:id"
            element={
              <Protegida>
                <PainelPaciente />
              </Protegida>
            }
          />
          <Route path="*" element={<Inicio />} />
        </Routes>
      </AuthProvider>
    </BrowserRouter>
  )
}
