import { describe, it, expect } from 'vitest';
import {
  USE_MOCKS,
  getRiscos,
  getAncestralidade,
  getHistorico,
} from './api';

describe('services/api (camada de mocks)', () => {
  it('está em modo mock enquanto os endpoints reais não existem', () => {
    expect(USE_MOCKS).toBe(true);
  });

  it('getRiscos retorna lista no formato do contrato', async () => {
    const riscos = await getRiscos('uuid-123');
    expect(Array.isArray(riscos)).toBe(true);
    expect(riscos.length).toBeGreaterThan(0);
    for (const r of riscos) {
      expect(r).toEqual(
        expect.objectContaining({
          painel: expect.any(String),
          caracteristica: expect.any(String),
          categoria_impacto: expect.any(String),
          conclusao_curta: expect.any(String),
          explicacao_detalhada: expect.any(String),
        }),
      );
      expect(Array.isArray(r.recomendacoes)).toBe(true);
    }
  });

  it('getAncestralidade retorna componentes marcados como ilustrativos', async () => {
    const dados = await getAncestralidade('uuid-123');
    expect(dados.ilustrativo).toBe(true);
    expect(Array.isArray(dados.componentes)).toBe(true);
    for (const c of dados.componentes) {
      expect(c).toEqual(
        expect.objectContaining({
          regiao: expect.any(String),
          percentual: expect.any(Number),
        }),
      );
    }
  });

  it('getHistorico retorna itens em ordem cronológica reversa', async () => {
    const itens = await getHistorico('uuid-123');
    expect(Array.isArray(itens)).toBe(true);
    expect(itens.length).toBeGreaterThan(0);
    for (const item of itens) {
      expect(item).toEqual(
        expect.objectContaining({
          id: expect.any(String),
          timestamp: expect.any(String),
          pergunta: expect.any(String),
          resposta: expect.any(String),
        }),
      );
    }
    // mais recente primeiro
    const ts = itens.map((i) => new Date(i.timestamp).getTime());
    const ordenadoDesc = [...ts].sort((a, b) => b - a);
    expect(ts).toEqual(ordenadoDesc);
  });
});
