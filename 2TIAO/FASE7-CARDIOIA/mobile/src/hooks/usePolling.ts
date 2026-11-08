import { useCallback, useEffect, useRef, useState } from 'react'
import { AppState } from 'react-native'
import { ApiError } from '../api/client'

/**
 * Busca `carregar` agora e a cada `intervaloMs`, só com o app em primeiro
 * plano. Mantém o último dado válido quando uma atualização falha.
 */
export function usePolling<T>(carregar: () => Promise<T>, intervaloMs: number) {
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
      if (AppState.currentState === 'active') void recarregar()
    }, intervaloMs)
    // ao voltar para o app, atualiza na hora
    const assinatura = AppState.addEventListener('change', (estado) => {
      if (estado === 'active') void recarregar()
    })
    return () => {
      clearInterval(id)
      assinatura.remove()
    }
  }, [carregar, intervaloMs, recarregar])

  return { dados, erro, carregando, atualizadoEm, recarregar }
}
