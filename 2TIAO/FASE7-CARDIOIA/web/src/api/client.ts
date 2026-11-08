import type {
  ChatRequest,
  ChatResponse,
  LoginRequest,
  LoginResponse,
  PacienteResumo,
  RespostaAtendimento,
  StatusPaciente,
} from './types'
import { ApiError } from './errors'
import { mockApi } from './mock'

const API_URL = (import.meta.env.VITE_API_URL ?? '').replace(/\/+$/, '')

/** Sem URL configurada (ou com VITE_USE_MOCK=true), o front usa dados simulados. */
export const USANDO_MOCK = import.meta.env.VITE_USE_MOCK === 'true' || API_URL === ''

/** O Render gratuito pode levar ~50 s para acordar; o timeout cobre esse caso. */
const TIMEOUT_MS = 70_000
/** A partir desse tempo de espera a UI avisa que o servidor está iniciando. */
const LENTO_APOS_MS = 4_000

export { ApiError }

// --- token de acesso -------------------------------------------------------

let token: string | null = null
let aoExpirarSessao: (() => void) | null = null

export function definirToken(novo: string | null): void {
  token = novo
}

export function aoReceber401(callback: (() => void) | null): void {
  aoExpirarSessao = callback
}

// --- aviso de servidor lento (cold start) ---------------------------------

type OuvinteLentidao = (lento: boolean) => void
const ouvintes = new Set<OuvinteLentidao>()
let pendentesLentas = 0

export function observarLentidao(ouvinte: OuvinteLentidao): () => void {
  ouvintes.add(ouvinte)
  ouvinte(pendentesLentas > 0)
  return () => ouvintes.delete(ouvinte)
}

function notificar(): void {
  for (const ouvinte of ouvintes) ouvinte(pendentesLentas > 0)
}

// --- requisição -------------------------------------------------------------

async function requisitar<T>(caminho: string, init: RequestInit = {}): Promise<T> {
  const controle = new AbortController()
  const timeout = setTimeout(() => controle.abort(), TIMEOUT_MS)
  let marcadoLento = false
  const lento = setTimeout(() => {
    marcadoLento = true
    pendentesLentas += 1
    notificar()
  }, LENTO_APOS_MS)

  const headers = new Headers(init.headers)
  headers.set('Accept', 'application/json')
  if (init.body) headers.set('Content-Type', 'application/json')
  if (token) headers.set('Authorization', `Bearer ${token}`)

  try {
    const resposta = await fetch(`${API_URL}${caminho}`, {
      ...init,
      headers,
      signal: controle.signal,
    })

    if (resposta.status === 401 && token) {
      aoExpirarSessao?.()
    }
    if (!resposta.ok) {
      throw new ApiError(resposta.status, await extrairMensagem(resposta))
    }
    return (await resposta.json()) as T
  } catch (erro) {
    if (erro instanceof ApiError) throw erro
    if (erro instanceof DOMException && erro.name === 'AbortError') {
      throw new ApiError(0, 'O servidor demorou demais para responder.')
    }
    throw new ApiError(0, 'Não foi possível conectar ao servidor.')
  } finally {
    clearTimeout(timeout)
    clearTimeout(lento)
    if (marcadoLento) {
      pendentesLentas -= 1
      notificar()
    }
  }
}

async function extrairMensagem(resposta: Response): Promise<string> {
  try {
    const corpo = (await resposta.json()) as { detail?: unknown }
    if (typeof corpo.detail === 'string') return corpo.detail
  } catch {
    // corpo não é JSON
  }
  if (resposta.status === 401) return 'Credenciais inválidas ou sessão expirada.'
  if (resposta.status === 404) return 'Recurso não encontrado.'
  return `Erro ${resposta.status} no servidor.`
}

const apiReal = {
  login: (dados: LoginRequest) =>
    requisitar<LoginResponse>('/api/auth/login', {
      method: 'POST',
      body: JSON.stringify(dados),
    }),
  listarPacientes: () => requisitar<PacienteResumo[]>('/api/pacientes'),
  obterStatus: (id: string) =>
    requisitar<StatusPaciente>(`/api/pacientes/${encodeURIComponent(id)}/status`),
  avaliar: (id: string) =>
    requisitar<RespostaAtendimento>(`/api/pacientes/${encodeURIComponent(id)}/avaliar`, {
      method: 'POST',
    }),
  enviarMensagem: (dados: ChatRequest) =>
    requisitar<ChatResponse>('/api/chat', {
      method: 'POST',
      body: JSON.stringify(dados),
    }),
}

export type Api = typeof apiReal

export const api: Api = USANDO_MOCK ? mockApi : apiReal
