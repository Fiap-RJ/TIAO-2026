import { useState, type FormEvent } from 'react'
import { Navigate, useNavigate } from 'react-router-dom'
import { ApiError, USANDO_MOCK } from '../api/client'
import { CREDENCIAIS_DEMO } from '../api/mock'
import { rotaInicial, useAuth } from '../auth/useAuth'
import { Logo } from '../components/Logo'

export function LoginPage() {
  const { usuario, entrar } = useAuth()
  const navegar = useNavigate()
  const [email, setEmail] = useState('')
  const [senha, setSenha] = useState('')
  const [erro, setErro] = useState<string | null>(null)
  const [enviando, setEnviando] = useState(false)

  if (usuario) return <Navigate to={rotaInicial(usuario)} replace />

  async function aoEnviar(evento: FormEvent) {
    evento.preventDefault()
    setErro(null)
    setEnviando(true)
    try {
      const logado = await entrar(email, senha)
      navegar(rotaInicial(logado), { replace: true })
    } catch (e) {
      setErro(e instanceof ApiError ? e.message : 'Não foi possível entrar.')
    } finally {
      setEnviando(false)
    }
  }

  return (
    <div className="login">
      <form className="cartao login-cartao" onSubmit={aoEnviar} noValidate>
        <div className="login-marca">
          <Logo tamanho={44} />
          <div>
            <h1>CardioIA</h1>
            <p>Plataforma de inteligência cardíaca</p>
          </div>
        </div>

        <label htmlFor="email">E-mail</label>
        <input
          id="email"
          type="email"
          autoComplete="username"
          value={email}
          onChange={(e) => setEmail(e.target.value)}
          required
        />

        <label htmlFor="senha">Senha</label>
        <input
          id="senha"
          type="password"
          autoComplete="current-password"
          value={senha}
          onChange={(e) => setSenha(e.target.value)}
          required
        />

        {erro && (
          <p className="erro" role="alert">
            {erro}
          </p>
        )}

        <button type="submit" className="botao botao-largo" disabled={enviando || !email || !senha}>
          {enviando ? 'Entrando…' : 'Entrar'}
        </button>

        {USANDO_MOCK && (
          <div className="demo">
            <p>Modo demonstração — use uma das contas:</p>
            {CREDENCIAIS_DEMO.map((c) => (
              <button
                key={c.email}
                type="button"
                className="chip chip-botao"
                onClick={() => {
                  setEmail(c.email)
                  setSenha(c.senha)
                }}
              >
                {c.perfil}: {c.email}
              </button>
            ))}
          </div>
        )}
      </form>
    </div>
  )
}
