/**
 * Client único de API do dashboard, consumindo o backend real (FastAPI).
 *
 * `API_BASE` vem de `VITE_API_BASE_URL`; vazio = URLs relativas, que funcionam
 * com o proxy do vite (dev) e do nginx (container). As funções adaptam o
 * contrato do backend ao formato que as páginas consomem, para que os
 * componentes não dependam dos nomes de campo do servidor.
 */
const API_BASE = import.meta.env.VITE_API_BASE_URL ?? '';

async function requisitar(caminho, opcoes = {}) {
  const url = `${API_BASE}${caminho}`;
  const resposta = await fetch(url, {
    ...opcoes,
    headers: { Accept: 'application/json', ...opcoes.headers },
  });
  if (!resposta.ok) {
    throw new Error(`Falha ao consultar ${url} (HTTP ${resposta.status})`);
  }
  return resposta;
}

async function getJson(caminho) {
  const resposta = await requisitar(caminho);
  return resposta.json();
}

const idCodificado = (pacienteId) => encodeURIComponent(pacienteId);

/**
 * GET /api/riscos/{paciente_id}
 * → { riscos: [{ painel, caracteristica, nivel, categoria_impacto, ... }],
 *     escala: [{ doenca, nivel, risco_calculado_percentual, intervalo_minimo,
 *               intervalo_maximo, classificacao_original }],
 *     laudoOrigem }
 * A lista de painéis do backend é achatada; `categoria_impacto` recebe a
 * categoria original do laudo (usada só como fallback quando falta `nivel`).
 */
export async function getRiscos(pacienteId) {
  const dados = await getJson(`/api/riscos/${idCodificado(pacienteId)}`);
  const paineis = dados.paineis ?? [];
  return {
    riscos: paineis.flatMap((p) =>
      (p.resultados ?? []).map((r) => ({
        painel: p.nome_painel,
        ...r,
        categoria_impacto: r.categoria_original,
      })),
    ),
    escala: dados.escala_risco_genetico ?? [],
    laudoOrigem: dados.laudo_origem,
  };
}

/**
 * GET /api/ancestralidade/{paciente_id}
 * → { componentes: [{ regiao, percentual }], observacao, ilustrativo: false }
 */
export async function getAncestralidade(pacienteId) {
  const dados = await getJson(`/api/ancestralidade/${idCodificado(pacienteId)}`);
  return {
    componentes: dados.composicao ?? [],
    observacao: dados.observacao ?? '',
    ilustrativo: false,
  };
}

/**
 * GET /api/historico/{paciente_id}
 * O backend devolve em ordem cronológica (mais antiga primeiro); aqui vira
 * [{ id: string, timestamp, pergunta, resposta, fontes }] do mais recente
 * para o mais antigo.
 */
export async function getHistorico(pacienteId) {
  const dados = await getJson(`/api/historico/${idCodificado(pacienteId)}`);
  return (dados.interacoes ?? [])
    .map((i) => ({ ...i, id: String(i.id), timestamp: i.criado_em }))
    .reverse();
}

/**
 * DELETE /api/historico/{paciente_id} — direito de exclusão (LGPD).
 * 204 (apagado) e 404 (nada a apagar) contam como sucesso.
 */
export async function deleteHistorico(pacienteId) {
  const url = `${API_BASE}/api/historico/${idCodificado(pacienteId)}`;
  const resposta = await fetch(url, { method: 'DELETE' });
  if (!resposta.ok && resposta.status !== 404) {
    throw new Error(`Falha ao apagar ${url} (HTTP ${resposta.status})`);
  }
}

/**
 * POST /api/chat/
 * → { resposta, fontes: [{ painel, marcador, gene, conclusao_curta }],
 *     painel_utilizado, guardrails_acionados: string[] }
 * `nivelDetalhe`: 'resumido' (padrão do backend) ou 'detalhado'.
 */
export async function postChat({ pacienteId, mensagem, nivelDetalhe }) {
  const corpo = { paciente_id: pacienteId, mensagem };
  if (nivelDetalhe) corpo.nivel_detalhe = nivelDetalhe;
  const resposta = await requisitar('/api/chat/', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(corpo),
  });
  return resposta.json();
}
