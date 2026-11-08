import { useCallback, useEffect, useMemo, useState, type ReactNode } from 'react'
import { aoReceber401, api, definirToken, USANDO_MOCK } from '../api/client'
import { restaurarSessaoMock } from '../api/mock'
import type { Usuario } from '../api/types'
import { AuthContext } from './contexto'

const CHAVE = 'cardioia.sessao'

interface Sessao {
  token: string
  usuario: Usuario
}

function lerSessao(): Sessao | null {
  try {
    const bruto = localStorage.getItem(CHAVE)
    return bruto ? (JSON.parse(bruto) as Sessao) : null
  } catch {
    return null
  }
}

function gravarSessao(sessao: Sessao | null): void {
  try {
    if (sessao) localStorage.setItem(CHAVE, JSON.stringify(sessao))
    else localStorage.removeItem(CHAVE)
  } catch {
    // armazenamento indisponível (aba anônima, bloqueio): a sessão vale só nesta aba
  }
}

function aplicarSessao(sessao: Sessao | null): void {
  definirToken(sessao?.token ?? null)
  if (USANDO_MOCK) restaurarSessaoMock(sessao?.usuario ?? null)
}

export function AuthProvider({ children }: { children: ReactNode }) {
  const [sessao, setSessao] = useState<Sessao | null>(() => {
    const salva = lerSessao()
    aplicarSessao(salva)
    return salva
  })

  const sair = useCallback(() => {
    aplicarSessao(null)
    gravarSessao(null)
    setSessao(null)
  }, [])

  useEffect(() => {
    aoReceber401(sair)
    return () => aoReceber401(null)
  }, [sair])

  const entrar = useCallback(async (email: string, senha: string) => {
    const resposta = await api.login({ email, senha })
    const nova = { token: resposta.access_token, usuario: resposta.usuario }
    aplicarSessao(nova)
    gravarSessao(nova)
    setSessao(nova)
    return resposta.usuario
  }, [])

  const valor = useMemo(
    () => ({ usuario: sessao?.usuario ?? null, entrar, sair }),
    [sessao, entrar, sair],
  )

  return <AuthContext.Provider value={valor}>{children}</AuthContext.Provider>
}
