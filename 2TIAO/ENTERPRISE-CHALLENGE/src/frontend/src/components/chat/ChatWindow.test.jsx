import { describe, it, expect, vi, afterEach } from 'vitest';
import { cleanup, render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import ChatWindow from './ChatWindow';
// Resposta real do backend (POST /api/chat/, modo resumido).
import chatFixture from '../../test/fixtures/chat.json';

const PERGUNTA = 'Como eu metabolizo a cafeína?';

function stubFetch(respostas) {
  const fila = [...respostas];
  const fetchMock = vi.fn(() => {
    const corpo = fila.shift() ?? chatFixture;
    return Promise.resolve({
      ok: true,
      status: 200,
      json: () => Promise.resolve(structuredClone(corpo)),
    });
  });
  vi.stubGlobal('fetch', fetchMock);
  return fetchMock;
}

const corpoDaChamada = (fetchMock, n) =>
  JSON.parse(fetchMock.mock.calls[n][1].body);

async function enviarPergunta(user) {
  await user.type(
    screen.getByPlaceholderText('Digite sua dúvida clínica...'),
    PERGUNTA,
  );
  await user.click(screen.getByRole('button', { name: /enviar/i }));
}

afterEach(() => {
  cleanup();
  vi.unstubAllGlobals();
  vi.restoreAllMocks();
});

describe('ChatWindow', () => {
  it('envia a pergunta no modo resumido e exibe painel e fontes', async () => {
    const fetchMock = stubFetch([chatFixture]);
    const user = userEvent.setup();
    render(<ChatWindow />);

    await enviarPergunta(user);

    expect(
      await screen.findByText(`Painel: ${chatFixture.painel_utilizado}`),
    ).toBeInTheDocument();
    expect(corpoDaChamada(fetchMock, 0)).toEqual({
      paciente_id: 'uuid-123',
      mensagem: PERGUNTA,
      nivel_detalhe: 'resumido',
    });
    expect(screen.getByText(/Fontes do laudo/)).toBeInTheDocument();
    expect(
      screen.queryByText('Resposta ajustada pelas salvaguardas'),
    ).not.toBeInTheDocument();
  });

  it('"Quero mais detalhes" reenvia a pergunta original no modo detalhado', async () => {
    const detalhada = {
      ...chatFixture,
      resposta: 'Explicação detalhada sobre a cafeína.',
    };
    const fetchMock = stubFetch([chatFixture, detalhada]);
    const user = userEvent.setup();
    render(<ChatWindow />);

    await enviarPergunta(user);
    await user.click(
      await screen.findByRole('button', { name: 'Quero mais detalhes' }),
    );

    expect(
      await screen.findByText('Explicação detalhada sobre a cafeína.'),
    ).toBeInTheDocument();
    expect(fetchMock).toHaveBeenCalledTimes(2);
    expect(corpoDaChamada(fetchMock, 1)).toEqual({
      paciente_id: 'uuid-123',
      mensagem: PERGUNTA,
      nivel_detalhe: 'detalhado',
    });
    // Resposta detalhada não oferece o botão de novo, e a resumida já foi usada.
    expect(
      screen.queryByRole('button', { name: 'Quero mais detalhes' }),
    ).not.toBeInTheDocument();
  });

  it('mantém "Quero mais detalhes" quando o pedido detalhado falha e permite tentar de novo', async () => {
    const detalhada = {
      ...chatFixture,
      resposta: 'Explicação detalhada sobre a cafeína.',
    };
    const respostas = [
      { ok: true, status: 200, corpo: chatFixture },
      { ok: false, status: 500, corpo: { detail: 'erro' } },
      { ok: true, status: 200, corpo: detalhada },
    ];
    const fetchMock = vi.fn(() => {
      const r = respostas.shift();
      return Promise.resolve({
        ok: r.ok,
        status: r.status,
        json: () => Promise.resolve(structuredClone(r.corpo)),
      });
    });
    vi.stubGlobal('fetch', fetchMock);
    vi.spyOn(console, 'error').mockImplementation(() => { });
    const user = userEvent.setup();
    render(<ChatWindow />);

    await enviarPergunta(user);
    await user.click(
      await screen.findByRole('button', { name: 'Quero mais detalhes' }),
    );

    // Falhou: mensagem de erro aparece e o botão continua disponível.
    expect(
      await screen.findByText(/Ocorreu um erro de conexão/),
    ).toBeInTheDocument();
    const botao = screen.getByRole('button', { name: 'Quero mais detalhes' });
    expect(botao).toBeEnabled();

    await user.click(botao);

    expect(
      await screen.findByText('Explicação detalhada sobre a cafeína.'),
    ).toBeInTheDocument();
    expect(fetchMock).toHaveBeenCalledTimes(3);
    expect(corpoDaChamada(fetchMock, 2).nivel_detalhe).toBe('detalhado');
    expect(
      screen.queryByRole('button', { name: 'Quero mais detalhes' }),
    ).not.toBeInTheDocument();
  });

  it('mostra aviso discreto quando guardrails foram acionados', async () => {
    stubFetch([{ ...chatFixture, guardrails_acionados: ['termo_proibido'] }]);
    const user = userEvent.setup();
    render(<ChatWindow />);

    await enviarPergunta(user);

    expect(
      await screen.findByText('Resposta ajustada pelas salvaguardas'),
    ).toBeInTheDocument();
  });

  it('mantém o controle de upload de PDF visível', () => {
    stubFetch([]);
    render(<ChatWindow />);
    expect(screen.getByText('Anexar Laudo PDF')).toBeInTheDocument();
  });
});
