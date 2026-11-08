// Cópia de web/src/api — mantenha os dois arquivos em sincronia.
/**
 * Backend simulado, usado enquanto a API real não está publicada
 * (ou com VITE_USE_MOCK=true).
 *
 * Reproduz o formato das respostas e uma versão simplificada das regras da
 * Fase 6 (regras do alvo, faixas de risco e protocolos P01–P10). A
 * probabilidade é heurística: o modelo de verdade só roda no backend.
 */
import { ApiError } from './errors'
import type {
  ChatRequest,
  ChatResponse,
  Classificacao,
  DadosPaciente,
  EstadoDispositivo,
  Leitura,
  LoginRequest,
  LoginResponse,
  Paciente,
  PacienteResumo,
  ProtocoloAcionado,
  RespostaAtendimento,
  SinalAtencao,
  StatusPaciente,
  Usuario,
} from './types'

const AVISO_LEGAL =
  'Aviso: o CardioIA é um sistema acadêmico, informativo e de apoio à decisão operacional, ' +
  'baseado em dados sintéticos. Não realiza diagnóstico, não prescreve tratamentos e não ' +
  'substitui a avaliação de um profissional de saúde.'

const INTERVALO_LEITURA_MS = 5_000
const MAX_LEITURAS = 60

// --- usuários e pacientes de demonstração ----------------------------------

const SENHA_DEMO = 'cardioia'

const USUARIOS: Record<string, Usuario> = {
  'medico@cardioia.com': {
    id: 'u-medico',
    nome: 'Dra. Helena Prado',
    perfil: 'medico',
    paciente_id: null,
  },
  'paciente@cardioia.com': {
    id: 'u-paciente',
    nome: 'João Batista',
    perfil: 'paciente',
    paciente_id: 'p-001',
  },
}

interface Simulado {
  paciente: Paciente
  /** Indicadores operacionais da unidade (não vêm do sensor). */
  operacional: Omit<DadosPaciente, 'fc_media' | 'spo2_media' | 'temperatura'>
  /** Valores-alvo para onde as leituras tendem. */
  alvo: { fc: number; spo2: number; temperatura: number }
  leituras: Leitura[]
  avaliacao: RespostaAtendimento | null
}

const simulados: Simulado[] = [
  {
    paciente: { id: 'p-001', nome: 'João Batista', idade: 62, leito: 'UTI-C 04' },
    operacional: {
      idade_media: 62,
      carga_sistema: 92,
      tempo_espera: 75,
      pa_sistolica: 100,
      densidade_eventos: 7,
      eventos_24h: 5,
      disponibilidade_recursos: 25,
    },
    alvo: { fc: 118, spo2: 89, temperatura: 37.5 },
    leituras: [],
    avaliacao: null,
  },
  {
    paciente: { id: 'p-002', nome: 'Maria Aparecida', idade: 71, leito: 'Enf. 12' },
    operacional: {
      idade_media: 71,
      carga_sistema: 84,
      tempo_espera: 40,
      pa_sistolica: 128,
      densidade_eventos: 3,
      eventos_24h: 2,
      disponibilidade_recursos: 55,
    },
    alvo: { fc: 104, spo2: 93, temperatura: 37.1 },
    leituras: [],
    avaliacao: null,
  },
  {
    paciente: { id: 'p-003', nome: 'Carlos Henrique', idade: 48, leito: 'Enf. 07' },
    operacional: {
      idade_media: 48,
      carga_sistema: 55,
      tempo_espera: 20,
      pa_sistolica: 122,
      densidade_eventos: 1,
      eventos_24h: 0,
      disponibilidade_recursos: 80,
    },
    alvo: { fc: 76, spo2: 98, temperatura: 36.6 },
    leituras: [],
    avaliacao: null,
  },
]

// --- simulação das leituras do sensor --------------------------------------

function arredondar(valor: number, casas = 1): number {
  const fator = 10 ** casas
  return Math.round(valor * fator) / fator
}

/** Id hexadecimal de 32 caracteres (sem depender de `crypto`, que falta em alguns runtimes mobile). */
function gerarId(): string {
  let id = ''
  for (let i = 0; i < 32; i++) id += Math.floor(Math.random() * 16).toString(16)
  return id
}

function ruido(amplitude: number): number {
  return (Math.random() * 2 - 1) * amplitude
}

/** Mesma classificação local feita pelo script MicroPython do dispositivo. */
function estadoLocal(fc: number, spo2: number, temperatura: number): EstadoDispositivo {
  if (fc > 120 || fc < 45 || spo2 < 90 || temperatura > 38.5) return 'critico'
  if (fc > 100 || fc < 55 || spo2 < 94 || temperatura > 37.8) return 'atencao'
  return 'normal'
}

function novaLeitura(sim: Simulado, ts: Date, anterior?: Leitura): Leitura {
  const base = anterior ?? { fc: sim.alvo.fc, spo2: sim.alvo.spo2, temperatura: sim.alvo.temperatura }
  // passeio aleatório puxado de volta para o alvo
  const fc = base.fc + (sim.alvo.fc - base.fc) * 0.3 + ruido(4)
  const spo2 = Math.min(100, base.spo2 + (sim.alvo.spo2 - base.spo2) * 0.3 + ruido(0.8))
  const temperatura = base.temperatura + (sim.alvo.temperatura - base.temperatura) * 0.3 + ruido(0.1)
  return {
    ts: ts.toISOString(),
    fc: Math.round(fc),
    spo2: Math.round(spo2),
    temperatura: arredondar(temperatura),
    estado: estadoLocal(fc, spo2, temperatura),
  }
}

function atualizarLeituras(sim: Simulado): boolean {
  const agora = Date.now()
  if (sim.leituras.length === 0) {
    // histórico inicial: 30 leituras, uma a cada 5 s
    for (let i = 30; i > 0; i--) {
      sim.leituras.push(
        novaLeitura(sim, new Date(agora - i * INTERVALO_LEITURA_MS), sim.leituras.at(-1)),
      )
    }
    return true
  }
  const ultima = sim.leituras.at(-1)!
  if (agora - Date.parse(ultima.ts) < INTERVALO_LEITURA_MS) return false
  sim.leituras.push(novaLeitura(sim, new Date(agora), ultima))
  if (sim.leituras.length > MAX_LEITURAS) sim.leituras.splice(0, sim.leituras.length - MAX_LEITURAS)
  return true
}

// --- regras simplificadas da Fase 6 ----------------------------------------

type Operador = '>' | '<'

const REGRAS_ALVO: Partial<Record<keyof DadosPaciente, [Operador, number]>> = {
  carga_sistema: ['>', 80],
  tempo_espera: ['>', 60],
  spo2_media: ['<', 92],
  fc_media: ['>', 110],
  eventos_24h: ['>', 4],
  disponibilidade_recursos: ['<', 40],
}

const PROTOCOLOS: { id: string; texto: string; variavel: keyof DadosPaciente; operador: Operador; limiar: number }[] = [
  { id: 'P01', texto: 'Se SPO2 < 88% → iniciar suporte respiratório imediato', variavel: 'spo2_media', operador: '<', limiar: 88 },
  { id: 'P02', texto: 'Se carga do sistema > 85% → abrir unidades temporárias', variavel: 'carga_sistema', operador: '>', limiar: 85 },
  { id: 'P03', texto: 'Se FC > 120 → iniciar monitoramento intensivo', variavel: 'fc_media', operador: '>', limiar: 120 },
  { id: 'P04', texto: 'Se eventos_24h > 5 → ativar equipe de resposta rápida', variavel: 'eventos_24h', operador: '>', limiar: 5 },
  { id: 'P05', texto: 'Se disponibilidade_recursos < 30% → redistribuir insumos', variavel: 'disponibilidade_recursos', operador: '<', limiar: 30 },
  { id: 'P06', texto: 'Se tempo_espera > 90 min → priorizar triagem emergencial', variavel: 'tempo_espera', operador: '>', limiar: 90 },
  { id: 'P07', texto: 'Se temperatura > 38°C média → iniciar protocolo infeccioso', variavel: 'temperatura', operador: '>', limiar: 38 },
  { id: 'P08', texto: 'Se densidade_eventos > 6 → ativar plano de contingência', variavel: 'densidade_eventos', operador: '>', limiar: 6 },
  { id: 'P09', texto: 'Se PA sistólica < 90 → iniciar protocolo de choque', variavel: 'pa_sistolica', operador: '<', limiar: 90 },
]

const ACOES: Record<string, string> = {
  P01: 'Iniciar suporte respiratório imediato.',
  P02: 'Abrir unidades temporárias para absorver a carga do sistema.',
  P03: 'Iniciar monitoramento intensivo da frequência cardíaca.',
  P04: 'Ativar a equipe de resposta rápida.',
  P05: 'Redistribuir insumos entre as unidades.',
  P06: 'Priorizar a triagem emergencial.',
  P07: 'Iniciar o protocolo infeccioso.',
  P08: 'Ativar o plano de contingência.',
  P09: 'Iniciar o protocolo de choque.',
  P10: 'Ativar o estado de emergência.',
}

function comparar(valor: number, operador: Operador, limiar: number): boolean {
  return operador === '>' ? valor > limiar : valor < limiar
}

function classificar(probabilidade: number): Classificacao {
  if (probabilidade >= 0.7) return 'ALTO'
  if (probabilidade >= 0.4) return 'MODERADO'
  return 'BAIXO'
}

function media(valores: number[]): number {
  return valores.reduce((soma, v) => soma + v, 0) / valores.length
}

function avaliar(sim: Simulado): RespostaAtendimento {
  const recentes = sim.leituras.slice(-6)
  const dados: DadosPaciente = {
    ...sim.operacional,
    fc_media: Math.round(media(recentes.map((l) => l.fc))),
    spo2_media: Math.round(media(recentes.map((l) => l.spo2))),
    temperatura: arredondar(media(recentes.map((l) => l.temperatura))),
  }

  const regras = Object.entries(REGRAS_ALVO) as [keyof DadosPaciente, [Operador, number]][]
  const verdadeiras = regras.filter(([nome, [op, lim]]) => comparar(dados[nome], op, lim)).length
  const probabilidade = arredondar(
    Math.min(0.99, [0.04, 0.46, 0.8, 0.93][Math.min(verdadeiras, 3)] + verdadeiras * 0.01),
    4,
  )
  const classificacao = classificar(probabilidade)

  const protocolos: ProtocoloAcionado[] = PROTOCOLOS.filter((p) =>
    comparar(dados[p.variavel], p.operador, p.limiar),
  ).map((p) => ({
    id: p.id,
    texto: p.texto,
    variavel: p.variavel,
    valor_observado: dados[p.variavel],
    limiar: p.limiar,
    justificativa: `${p.variavel}=${dados[p.variavel]} ${p.operador} ${p.limiar}`,
  }))
  if (classificacao === 'ALTO') {
    protocolos.push({
      id: 'P10',
      texto: 'Se risco sistêmico alto → ativar estado de emergência',
      variavel: 'classificacao_risco',
      valor_observado: 'ALTO',
      limiar: 'ALTO',
      justificativa: 'classificacao_risco=ALTO',
    })
  }

  const sinais: SinalAtencao[] = []
  for (const p of PROTOCOLOS) {
    const regra = REGRAS_ALVO[p.variavel]
    if (!regra) continue
    const valor = dados[p.variavel]
    if (comparar(valor, regra[0], regra[1]) && !comparar(valor, p.operador, p.limiar)) {
      sinais.push({
        variavel: p.variavel,
        valor,
        limiar_risco: regra[1],
        limiar_protocolo: p.limiar,
        protocolo_id: p.id,
        mensagem: `${p.variavel}=${valor} (risco ${regra[0]} ${regra[1]}; ${p.id} aciona ${p.operador} ${p.limiar})`,
      })
    }
  }

  const acoes = protocolos.map((p) => ACOES[p.id])
  for (const s of sinais) acoes.push(`Monitorar ${s.variavel} (${s.valor}), próximo do gatilho do ${s.protocolo_id}.`)
  if (acoes.length === 0) acoes.push('Manter o monitoramento de rotina.')

  return {
    atendimento_id: gerarId(),
    gerado_em: new Date().toISOString(),
    paciente: dados,
    avaliacao_risco: {
      probabilidade,
      classificacao,
      pico_risco_previsto: probabilidade >= 0.5,
      limiar_decisao: 0.5,
      modelo_versao: 'simulado',
      avisos: [],
    },
    protocolos,
    sinais_de_atencao: sinais,
    acoes_operacionais: acoes.slice(0, 8),
    explicacao:
      `Risco ${classificacao.toLowerCase()} (p=${probabilidade.toFixed(2)}): ${verdadeiras} de 6 ` +
      'indicadores de risco acima do limiar. Explicação gerada pelo modo simulado do front-end; ' +
      'com o backend publicado, este texto é redigido pelos agentes da Fase 6.',
    cadeia_agentes: [],
    origem: 'sem_llm',
    violacoes_guardrail: [],
    motivo_fallback: null,
    aviso_legal: AVISO_LEGAL,
  }
}

// --- helpers da API simulada ------------------------------------------------

let usuarioLogado: Usuario | null = null

/** Restaura a sessão simulada após recarregar a página (o token fica no navegador). */
export function restaurarSessaoMock(usuario: Usuario | null): void {
  usuarioLogado = usuario
}

function atraso<T>(valor: T, ms = 250): Promise<T> {
  // cópia profunda: a tela nunca recebe referência ao estado interno da simulação
  return new Promise((resolve) => setTimeout(() => resolve(JSON.parse(JSON.stringify(valor)) as T), ms))
}

function exigirLogin(): Usuario {
  if (!usuarioLogado) throw new ApiError(401, 'Sessão expirada. Entre novamente.')
  return usuarioLogado
}

function buscar(id: string): Simulado {
  const usuario = exigirLogin()
  const sim = simulados.find((s) => s.paciente.id === id)
  if (!sim) throw new ApiError(404, 'Paciente não encontrado.')
  if (usuario.perfil === 'paciente' && usuario.paciente_id !== id) {
    throw new ApiError(403, 'Acesso negado a este paciente.')
  }
  return sim
}

function tick(sim: Simulado): void {
  // a cada leitura nova o backend reavalia o risco automaticamente
  if (atualizarLeituras(sim) || !sim.avaliacao) sim.avaliacao = avaliar(sim)
}

function respostaChat(mensagem: string): string {
  const texto = mensagem.toLowerCase()
  if (/(dose|dosagem|medicamento|rem[eé]dio|prescrev)/.test(texto)) {
    return 'O CardioIA é informativo e não indica medicamentos, prescrições ou doses. Consulte um profissional de saúde.'
  }
  if (/(dor no peito|aperto|falta de ar|desmaio)/.test(texto)) {
    return 'Dor no peito, falta de ar ou desmaio podem indicar uma emergência. Procure atendimento imediatamente ou ligue 192 (SAMU).'
  }
  if (/(risco|probabilidade|classifica)/.test(texto)) {
    return 'A classificação de risco vem do modelo preditivo: BAIXO abaixo de 0,40, MODERADO entre 0,40 e 0,70 e ALTO a partir de 0,70.'
  }
  if (/(protocolo)/.test(texto)) {
    return 'Os protocolos P01 a P10 são acionados quando um indicador passa do limiar. A lista ao lado mostra quais foram acionados e por quê.'
  }
  return 'Sou o assistente da CardioIA (modo simulado). Posso explicar os indicadores, a classificação de risco e os protocolos sugeridos.'
}

export const mockApi = {
  async login({ email, senha }: LoginRequest): Promise<LoginResponse> {
    const usuario = USUARIOS[email.trim().toLowerCase()]
    if (!usuario || senha !== SENHA_DEMO) {
      await atraso(null, 400)
      throw new ApiError(401, 'E-mail ou senha inválidos.')
    }
    usuarioLogado = usuario
    return atraso({ access_token: `mock-${usuario.id}`, token_type: 'bearer', usuario }, 400)
  },

  async listarPacientes(): Promise<PacienteResumo[]> {
    const usuario = exigirLogin()
    const visiveis =
      usuario.perfil === 'medico'
        ? simulados
        : simulados.filter((s) => s.paciente.id === usuario.paciente_id)
    return atraso(
      visiveis.map((sim) => {
        tick(sim)
        return {
          ...sim.paciente,
          ultima_leitura: sim.leituras.at(-1) ?? null,
          probabilidade: sim.avaliacao?.avaliacao_risco.probabilidade ?? null,
          classificacao: sim.avaliacao?.avaliacao_risco.classificacao ?? null,
          avaliado_em: sim.avaliacao?.gerado_em ?? null,
        }
      }),
    )
  },

  async obterStatus(id: string): Promise<StatusPaciente> {
    const sim = buscar(id)
    tick(sim)
    return atraso({ paciente: sim.paciente, leituras: sim.leituras, avaliacao: sim.avaliacao })
  },

  async avaliar(id: string): Promise<RespostaAtendimento> {
    const sim = buscar(id)
    atualizarLeituras(sim)
    sim.avaliacao = avaliar(sim)
    return atraso(sim.avaliacao, 900)
  },

  async enviarMensagem({ mensagem, sessao_id }: ChatRequest): Promise<ChatResponse> {
    exigirLogin()
    return atraso(
      { resposta: respostaChat(mensagem), sessao_id: sessao_id ?? gerarId(), origem: 'fallback' },
      700,
    )
  },
}

/** Credenciais exibidas na tela de login quando o modo simulado está ativo. */
export const CREDENCIAIS_DEMO = [
  { perfil: 'Médico', email: 'medico@cardioia.com', senha: SENHA_DEMO },
  { perfil: 'Paciente', email: 'paciente@cardioia.com', senha: SENHA_DEMO },
]
