import { describe, it, expect } from 'vitest';
import {
  getRiskLevel,
  CATEGORIA_PARA_NIVEL,
  NIVEIS,
} from './riskLevelMap';

describe('riskLevelMap', () => {
  it('mapeia as categorias conhecidas do laudo para níveis neutros', () => {
    expect(getRiskLevel('Cuidados relevantes').nivel).toBe('baixo');
    expect(getRiskLevel('Pontos de atenção').nivel).toBe('moderado');
    expect(getRiskLevel('Intervenção médica recomendada').nivel).toBe(
      'atencao',
    );
  });

  it('usa rótulos legíveis para cada nível', () => {
    expect(getRiskLevel('Cuidados relevantes').label).toBe('Baixo');
    expect(getRiskLevel('Pontos de atenção').label).toBe('Moderado');
    expect(getRiskLevel('Intervenção médica recomendada').label).toBe(
      'Atenção',
    );
  });

  it('cai em "moderado" (neutro) para categorias desconhecidas', () => {
    expect(getRiskLevel('Categoria inexistente').nivel).toBe('moderado');
    expect(getRiskLevel(undefined).nivel).toBe('moderado');
  });

  it('nunca usa cores alarmistas (vermelho puro) na paleta', () => {
    for (const nivel of Object.values(NIVEIS)) {
      expect(nivel.badgeClasses).not.toMatch(/\bbg-red-/);
      expect(nivel.badgeClasses).not.toMatch(/\btext-red-/);
    }
  });

  it('cobre todas as categorias observadas nos dados estruturados', () => {
    expect(Object.keys(CATEGORIA_PARA_NIVEL)).toEqual(
      expect.arrayContaining([
        'Cuidados relevantes',
        'Pontos de atenção',
        'Intervenção médica recomendada',
      ]),
    );
  });
});
