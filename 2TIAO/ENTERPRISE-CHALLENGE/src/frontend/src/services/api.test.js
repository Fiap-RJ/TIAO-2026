import { describe, it, expect, vi, afterEach } from 'vitest';
import {
  getRiscos,
  getAncestralidade,
  getHistorico,
  deleteHistorico,
  postChat,
} from './api';
// Fixtures copiadas de respostas reais do backend (GET/POST em localhost:8000).
import riscosFixture from '../test/fixtures/riscos.json';
import ancestralidadeFixture from '../test/fixtures/ancestralidade.json';
import historicoFixture from '../test/fixtures/historico.json';
import chatFixture from '../test/fixtures/chat.json';

function respostaJson(corpo, status = 200) {
  return {
    ok: status >= 200 && status < 300,
    status,
    json: () => Promise.resolve(structuredClone(corpo)),
  };
}

function stubFetch(resposta) {
  const fetchMock = vi.fn(() => Promise.resolve(resposta));
  vi.stubGlobal('fetch', fetchMock);
  return fetchMock;
}

afterEach(() => {
  vi.unstubAllGlobals();
});

describe('services/api (contrato real do backend)', () => {
  it('getRiscos chama a rota do paciente e achata os painéis', async () => {
    const fetchMock = stubFetch(respostaJson(riscosFixture));

    const dados = await getRiscos('uuid-123');

    expect(fetchMock).toHaveBeenCalledWith(
      '/api/riscos/uuid-123',
      expect.any(Object),
    );
    const totalResultados = riscosFixture.paineis.reduce(
      (soma, p) => soma + p.resultados.length,
      0,
    );
    expect(dados.riscos).toHaveLength(totalResultados);

    const primeiroPainel = riscosFixture.paineis[0];
    const primeiroResultado = primeiroPainel.resultados[0];
    expect(dados.riscos[0]).toEqual({
      painel: primeiroPainel.nome_painel,
      ...primeiroResultado,
      categoria_impacto: primeiroResultado.categoria_original,
    });
    expect(dados.escala).toEqual(riscosFixture.escala_risco_genetico);
    expect(dados.laudoOrigem).toBe(riscosFixture.laudo_origem);
  });

  it('getAncestralidade mapeia composicao e observacao', async () => {
    stubFetch(respostaJson(ancestralidadeFixture));

    const dados = await getAncestralidade('uuid-123');

    expect(dados).toEqual({
      componentes: ancestralidadeFixture.composicao,
      observacao: ancestralidadeFixture.observacao,
      ilustrativo: false,
    });
  });

  it('getHistorico inverte a ordem e normaliza id/timestamp', async () => {
    stubFetch(respostaJson(historicoFixture));

    const itens = await getHistorico('uuid-123');

    const origem = historicoFixture.interacoes;
    expect(origem.length).toBeGreaterThan(1);
    expect(itens).toHaveLength(origem.length);
    expect(itens[0].id).toBe(String(origem[origem.length - 1].id));
    for (const item of itens) {
      expect(typeof item.id).toBe('string');
      expect(item.timestamp).toBe(item.criado_em);
    }
    // mais recente primeiro
    const ts = itens.map((i) => new Date(i.timestamp).getTime());
    expect(ts).toEqual([...ts].sort((a, b) => b - a));
  });

  it('propaga erro HTTP com status na mensagem', async () => {
    stubFetch(respostaJson({ detail: 'erro' }, 500));
    await expect(getRiscos('uuid-123')).rejects.toThrow('HTTP 500');
  });

  it('postChat envia paciente_id, mensagem e nivel_detalhe', async () => {
    const fetchMock = stubFetch(respostaJson(chatFixture));

    const dados = await postChat({
      pacienteId: 'uuid-123',
      mensagem: 'Como eu metabolizo a cafeína?',
      nivelDetalhe: 'detalhado',
    });

    expect(dados).toEqual(chatFixture);
    const [url, opcoes] = fetchMock.mock.calls[0];
    expect(url).toBe('/api/chat/');
    expect(opcoes.method).toBe('POST');
    expect(JSON.parse(opcoes.body)).toEqual({
      paciente_id: 'uuid-123',
      mensagem: 'Como eu metabolizo a cafeína?',
      nivel_detalhe: 'detalhado',
    });
  });

  it.each([204, 404])(
    'deleteHistorico trata HTTP %i como sucesso',
    async (status) => {
      const fetchMock = stubFetch({ ok: status === 204, status });
      await expect(deleteHistorico('uuid-123')).resolves.toBeUndefined();
      expect(fetchMock).toHaveBeenCalledWith('/api/historico/uuid-123', {
        method: 'DELETE',
      });
    },
  );

  it('deleteHistorico falha em outros erros HTTP', async () => {
    stubFetch({ ok: false, status: 500 });
    await expect(deleteHistorico('uuid-123')).rejects.toThrow('HTTP 500');
  });
});
