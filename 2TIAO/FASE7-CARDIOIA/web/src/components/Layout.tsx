import { useEffect, useState, type ReactNode } from 'react'
import { Link } from 'react-router-dom'
import { observarLentidao, USANDO_MOCK } from '../api/client'
import { rotaInicial, useAuth } from '../auth/useAuth'
import { Logo } from './Logo'

export function Layout({ children }: { children: ReactNode }) {
  const { usuario, sair } = useAuth()
  const [lento, setLento] = useState(false)

  useEffect(() => observarLentidao(setLento), [])

  return (
    <div className="app">
      <header className="topbar">
        <Link to={usuario ? rotaInicial(usuario) : '/'} className="marca" aria-label="CardioIA — início">
          <Logo />
          <span>CardioIA</span>
        </Link>
        {USANDO_MOCK && (
          <span className="chip chip-neutro" title="Sem backend configurado: dados simulados no navegador">
            Modo demonstração
          </span>
        )}
        {usuario && (
          <div className="usuario">
            <span className="usuario-nome">
              {usuario.nome}
              <small>{usuario.perfil === 'medico' ? 'Médico(a)' : 'Paciente'}</small>
            </span>
            <button type="button" className="botao botao-secundario" onClick={sair}>
              Sair
            </button>
          </div>
        )}
      </header>
      {lento && (
        <div className="faixa-aviso" role="status">
          O servidor está iniciando (pode levar até um minuto na primeira chamada)…
        </div>
      )}
      <main className="conteudo">{children}</main>
    </div>
  )
}
