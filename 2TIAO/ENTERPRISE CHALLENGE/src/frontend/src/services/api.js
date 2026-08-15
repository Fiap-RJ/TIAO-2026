/**
 * Client único de API do dashboard.
 *
 * Hoje as funções leem de mocks locais (`src/mocks/`) porque os endpoints do
 * backend (M1–M4, responsabilidade do Michael) ainda não existem. Quando eles
 * ficarem prontos, basta virar a flag `USE_MOCKS` para `false`: as assinaturas
 * das funções e o formato de retorno já seguem os contratos da seção 3 do
 * spec, então os componentes não precisam mudar.
 *
 * Cada tarefa acrescenta sua função aqui: A2 → getRiscos, A4 → getHistorico,
 * A3 → getAncestralidade.
 */
import riscosMock from '../mocks/riscos.mock.json';
import ancestralidadeMock from '../mocks/ancestralidade.mock.json';

// Ponto de troca mock → real. Vire para `false` quando os endpoints existirem.
export const USE_MOCKS = true;

// Pequeno atraso para simular latência de rede e permitir testar loading states.
const MOCK_DELAY_MS = 300;

function mockResponse(data) {
  return new Promise((resolve) => {
    setTimeout(() => resolve(structuredClone(data)), MOCK_DELAY_MS);
  });
}

async function getJson(url) {
  const resposta = await fetch(url, {
    headers: { Accept: 'application/json' },
  });
  if (!resposta.ok) {
    throw new Error(`Falha ao consultar ${url} (HTTP ${resposta.status})`);
  }
  return resposta.json();
}

/** GET /api/riscos/{paciente_id} */
export async function getRiscos(pacienteId) {
  if (USE_MOCKS) return mockResponse(riscosMock);
  return getJson(`/api/riscos/${pacienteId}`);
}

/**
 * GET /api/ancestralidade/{paciente_id}
 * Formato provisório (ver seção 2 do spec): { componentes: [{ regiao, percentual }] }.
 * O mock traz `ilustrativo: true` porque a fonte estruturada ainda não expõe
 * ancestralidade — dado fictício apenas para demonstração da UI.
 */
export async function getAncestralidade(pacienteId) {
  if (USE_MOCKS) return mockResponse(ancestralidadeMock);
  return getJson(`/api/ancestralidade/${pacienteId}`);
}
