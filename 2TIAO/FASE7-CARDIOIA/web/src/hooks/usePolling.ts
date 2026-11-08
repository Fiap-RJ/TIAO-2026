import { useCallback, useEffect, useRef, useState } from 'react'
import { ApiError } from '../api/client'

interface EstadoPolling<T> {
  dados: T | null
  erro: string | null
  carregando: boolean
  atualizadoEm: Date | null
  recarregar: () => Promise<void>
}

/**
 * Busca `carregar` agora e a cada `intervaloMs`. Pausa com a aba oculta e
 * mantém o último dado válido quando uma atualização falha. Para trocar de
 * recurso (ex.: outro paciente), remonte o componente com uma `key` nova.
 */
export function usePolling<T>(carregar: () => Promise<T>, intervaloMs: number): EstadoPolling<T> {
  const [dados, setDados] = useState<T | null>(null)
  const [erro, setErro] = useState<string | null>(null)
  const [carregando, setCarregando] = useState(true)
  const [atualizadoEm, setAtualizadoEm] = useState<Date | null>(null)
  const emAndamento = useRef(false)
  const carregarRef = useRef(carregar)

  useEffect(() => {
    carregarRef.current = carregar
  }, [carregar])

  const recarregar = useCallback(async () => {
    if (emAndamento.current) return
    emAndamento.current = true
    try {
      setDados(await carregarRef.current())
      setErro(null)
      setAtualizadoEm(new Date())
    } catch (e) {
      setErro(e instanceof ApiError ? e.message : 'Erro inesperado ao carregar os dados.')
    } finally {
      emAndamento.current = false
      setCarregando(false)
    }
  }, [])

  useEffect(() => {
    void recarregar()
    const id = setInterval(() => {
      if (document.visibilityState === 'visible') void recarregar()
    }, intervaloMs)
    return () => clearInterval(id)
  }, [carregar, intervaloMs, recarregar])

  return { dados, erro, carregando, atualizadoEm, recarregar }
}
