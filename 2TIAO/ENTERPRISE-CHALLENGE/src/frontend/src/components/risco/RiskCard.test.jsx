import { describe, it, expect, afterEach } from 'vitest';
import { cleanup, render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import RiskCard from './RiskCard';

const RISCO = {
  painel: 'Genera Nutri',
  caracteristica: 'Sensibilidade à Cafeína',
  categoria_impacto: 'Pontos de atenção',
  conclusao_curta: 'Metabolismo mais lento de cafeína',
  explicacao_detalhada: 'Seu genótipo indica metabolização mais lenta.',
  recomendacoes: ['Moderar consumo à tarde', 'Conversar com profissional'],
};

afterEach(cleanup);

describe('RiskCard', () => {
  it('renderiza característica, nível e conclusão curta', () => {
    render(<RiskCard risco={RISCO} />);
    expect(
      screen.getByRole('heading', { name: 'Sensibilidade à Cafeína' }),
    ).toBeInTheDocument();
    expect(screen.getByText('Moderado')).toBeInTheDocument();
    expect(
      screen.getByText('Metabolismo mais lento de cafeína'),
    ).toBeInTheDocument();
  });

  it('mantém os detalhes ocultos até o usuário expandir', () => {
    render(<RiskCard risco={RISCO} />);
    expect(
      screen.queryByText(RISCO.explicacao_detalhada),
    ).not.toBeInTheDocument();

    const botao = screen.getByRole('button', { name: 'Ver detalhes' });
    expect(botao).toHaveAttribute('aria-expanded', 'false');
  });

  it('expande e mostra explicação e recomendações ao clicar', async () => {
    const user = userEvent.setup();
    render(<RiskCard risco={RISCO} />);

    await user.click(screen.getByRole('button', { name: 'Ver detalhes' }));

    expect(screen.getByText(RISCO.explicacao_detalhada)).toBeInTheDocument();
    expect(screen.getByText('Moderar consumo à tarde')).toBeInTheDocument();
    expect(
      screen.getByRole('button', { name: 'Ocultar detalhes' }),
    ).toHaveAttribute('aria-expanded', 'true');
  });
});
