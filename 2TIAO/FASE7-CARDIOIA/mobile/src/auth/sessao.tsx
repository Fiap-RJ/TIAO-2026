import * as SecureStore from 'expo-secure-store'
import {
  createContext,
  useCallback,
  useContext,
  useEffect,
  useMemo,
  useState,
  type ReactNode,
} from 'react'
import { aoReceber401, api, definirToken, USANDO_MOCK } from '../api/client'
import { restaurarSessaoMock } from '../api/mock'
import type { Usuario } from '../api/types'

const CHAVE = 'cardioia.sessao'

interface Sessao {
  token: string
  usuario: Usuario
}

interface SessaoValor {
  usuario: Usuario | null
  /** true enquanto a sessão salva no aparelho está sendo lida. */
  carregando: boolean
  entrar: (email: string, senha: string) => Promise<Usuario>
  sair: () => void
}

const SessaoContext = createContext<SessaoValor | null>(null)

function aplicar(sessao: Sessao | null): void {
  definirToken(sessao?.token ?? null)
  if (USANDO_MOCK) restaurarSessaoMock(sessao?.usuario ?? null)
}

async function gravar(sessao: Sessao | null): Promise<void> {
  try {
    if (sessao) await SecureStore.setItemAsync(CHAVE, JSON.stringify(sessao))
    else await SecureStore.deleteItemAsync(CHAVE)
  } catch {
    // armazenamento seguro indisponível: a sessão vale só enquanto o app estiver aberto
  }
}

export function SessaoProvider({ children }: { children: ReactNode }) {
  const [sessao, setSessao] = useState<Sessao | null>(null)
  const [carregando, setCarregando] = useState(true)

  useEffect(() => {
    let ativo = true
    SecureStore.getItemAsync(CHAVE)
      .then((bruto) => (bruto ? (JSON.parse(bruto) as Sessao) : null))
      .catch(() => null)
      .then((salva) => {
        if (!ativo) return
        aplicar(salva)
        setSessao(salva)
        setCarregando(false)
      })
    return () => {
      ativo = false
    }
  }, [])

  const sair = useCallback(() => {
    aplicar(null)
    setSessao(null)
    void gravar(null)
  }, [])

  useEffect(() => {
    aoReceber401(sair)
    return () => aoReceber401(null)
  }, [sair])

  const entrar = useCallback(async (email: string, senha: string) => {
    const resposta = await api.login({ email, senha })
    const nova = { token: resposta.access_token, usuario: resposta.usuario }
    aplicar(nova)
    setSessao(nova)
    await gravar(nova)
    return resposta.usuario
  }, [])

  const valor = useMemo(
    () => ({ usuario: sessao?.usuario ?? null, carregando, entrar, sair }),
    [sessao, carregando, entrar, sair],
  )

  return <SessaoContext.Provider value={valor}>{children}</SessaoContext.Provider>
}

export function useSessao(): SessaoValor {
  const valor = useContext(SessaoContext)
  if (!valor) throw new Error('useSessao precisa estar dentro de <SessaoProvider>')
  return valor
}

export function rotaInicial(usuario: Usuario): '/pacientes' | `/pacientes/${string}` {
  return usuario.perfil === 'paciente' && usuario.paciente_id
    ? `/pacientes/${usuario.paciente_id}`
    : '/pacientes'
}
