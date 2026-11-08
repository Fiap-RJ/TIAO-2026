import type { Classificacao, EstadoDispositivo, OrigemRecomendacao } from '../api/types'

export const ROTULO_FAIXA: Record<Classificacao, string> = {
  BAIXO: 'Risco baixo',
  MODERADO: 'Risco moderado',
  ALTO: 'Risco alto',
}

export const ROTULO_ESTADO: Record<EstadoDispositivo, string> = {
  normal: 'Normal',
  atencao: 'Atenção',
  critico: 'Crítico',
}

export const ROTULO_ORIGEM: Record<OrigemRecomendacao, string> = {
  agentes: 'Agentes de IA',
  fallback_deterministico: 'Regras determinísticas (fallback)',
  sem_llm: 'Regras determinísticas',
}

/** Nomes legíveis das features do modelo da Fase 6. */
export const ROTULO_VARIAVEL: Record<string, string> = {
  idade_media: 'Idade média',
  carga_sistema: 'Carga do sistema',
  tempo_espera: 'Tempo de espera',
  fc_media: 'FC média',
  spo2_media: 'SpO₂ média',
  pa_sistolica: 'PA sistólica',
  temperatura: 'Temperatura',
  densidade_eventos: 'Densidade de eventos',
  eventos_24h: 'Eventos em 24 h',
  disponibilidade_recursos: 'Disponibilidade de recursos',
  classificacao_risco: 'Classificação de risco',
}

export const UNIDADE_VARIAVEL: Record<string, string> = {
  idade_media: 'anos',
  carga_sistema: '%',
  tempo_espera: 'min',
  fc_media: 'bpm',
  spo2_media: '%',
  pa_sistolica: 'mmHg',
  temperatura: '°C',
  disponibilidade_recursos: '%',
}

const numero = new Intl.NumberFormat('pt-BR', { maximumFractionDigits: 1 })
const hora = new Intl.DateTimeFormat('pt-BR', { hour: '2-digit', minute: '2-digit', second: '2-digit' })

export function formatarNumero(valor: number): string {
  return numero.format(valor)
}

export function formatarPercentual(probabilidade: number): string {
  return `${Math.round(probabilidade * 100)}%`
}

export function formatarHora(iso: string | Date): string {
  return hora.format(typeof iso === 'string' ? new Date(iso) : iso)
}

export function tempoRelativo(iso: string): string {
  const segundos = Math.max(0, Math.round((Date.now() - Date.parse(iso)) / 1000))
  if (segundos < 10) return 'agora'
  if (segundos < 60) return `há ${segundos} s`
  const minutos = Math.round(segundos / 60)
  if (minutos < 60) return `há ${minutos} min`
  return `às ${formatarHora(iso)}`
}
