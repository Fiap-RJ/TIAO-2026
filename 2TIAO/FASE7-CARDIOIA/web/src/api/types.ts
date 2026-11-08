/**
 * Contrato da API do backend integrador CardioIA.
 *
 * `RespostaAtendimento` e seus filhos espelham os schemas Pydantic da Fase 6
 * (`domain/schemas.py`), para que o backend possa devolver a saída do pipeline
 * sem conversão.
 */

export type Perfil = 'medico' | 'paciente'
export type Classificacao = 'BAIXO' | 'MODERADO' | 'ALTO'
export type EstadoDispositivo = 'normal' | 'atencao' | 'critico'
export type OrigemRecomendacao = 'agentes' | 'fallback_deterministico' | 'sem_llm'
export type OrigemChat = 'watson' | 'openai' | 'fallback'

export interface Usuario {
  id: string
  nome: string
  perfil: Perfil
  /** Preenchido quando o perfil é `paciente`. */
  paciente_id: string | null
}

export interface LoginRequest {
  email: string
  senha: string
}

export interface LoginResponse {
  access_token: string
  token_type: 'bearer'
  usuario: Usuario
}

/** Leitura enviada pelo dispositivo (ESP32/MicroPython). */
export interface Leitura {
  ts: string
  temperatura: number
  fc: number
  spo2: number
  /** Classificação local feita no dispositivo. */
  estado: EstadoDispositivo
}

export interface Paciente {
  id: string
  nome: string
  idade: number
  leito: string
}

export interface PacienteResumo extends Paciente {
  ultima_leitura: Leitura | null
  probabilidade: number | null
  classificacao: Classificacao | null
  avaliado_em: string | null
}

export interface DadosPaciente {
  idade_media: number
  carga_sistema: number
  tempo_espera: number
  fc_media: number
  spo2_media: number
  pa_sistolica: number
  temperatura: number
  densidade_eventos: number
  eventos_24h: number
  disponibilidade_recursos: number
}

export interface AvaliacaoRisco {
  probabilidade: number
  classificacao: Classificacao
  pico_risco_previsto: boolean
  limiar_decisao: number
  modelo_versao: string
  avisos: string[]
}

export interface ProtocoloAcionado {
  id: string
  texto: string
  variavel: string
  valor_observado: number | string
  limiar: number | string
  justificativa: string
}

export interface SinalAtencao {
  variavel: string
  valor: number
  limiar_risco: number
  limiar_protocolo: number
  protocolo_id: string
  mensagem: string
}

export interface RespostaAtendimento {
  atendimento_id: string
  gerado_em: string
  paciente: DadosPaciente
  avaliacao_risco: AvaliacaoRisco
  protocolos: ProtocoloAcionado[]
  sinais_de_atencao: SinalAtencao[]
  acoes_operacionais: string[]
  explicacao: string
  cadeia_agentes: string[]
  origem: OrigemRecomendacao
  violacoes_guardrail: string[]
  motivo_fallback: string | null
  aviso_legal: string
}

export interface StatusPaciente {
  paciente: Paciente
  /** Ordem cronológica crescente (a mais recente por último). */
  leituras: Leitura[]
  avaliacao: RespostaAtendimento | null
}

export interface ChatRequest {
  mensagem: string
  paciente_id: string | null
  sessao_id: string | null
}

export interface ChatResponse {
  resposta: string
  sessao_id: string
  origem: OrigemChat
}

export interface HealthResponse {
  status: 'ok'
}
