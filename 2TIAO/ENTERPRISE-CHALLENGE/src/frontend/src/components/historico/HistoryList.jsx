import { useState } from 'react';
import MessageBubble from '../chat/MessageBubble';

const ITENS_POR_PAGINA = 10;

function formatarData(iso) {
  const data = new Date(iso);
  if (Number.isNaN(data.getTime())) return '';
  return data.toLocaleString('pt-BR', {
    dateStyle: 'short',
    timeStyle: 'short',
  });
}

/**
 * HistoryList — lista cronológica reversa de interações (A4), com paginação
 * client-side. Cada item mostra a pergunta do paciente e a resposta da IA
 * reaproveitando o MessageBubble do chat.
 *
 * Assume que `itens` já vem do mais recente para o mais antigo (ver contrato).
 */
export default function HistoryList({ itens }) {
  const [pagina, setPagina] = useState(1);

  const totalPaginas = Math.max(1, Math.ceil(itens.length / ITENS_POR_PAGINA));
  const paginaAtual = Math.min(pagina, totalPaginas);
  const inicio = (paginaAtual - 1) * ITENS_POR_PAGINA;
  const visiveis = itens.slice(inicio, inicio + ITENS_POR_PAGINA);

  return (
    <div>
      <ol className="space-y-6">
        {visiveis.map((item) => (
          <li
            key={item.id}
            className="rounded-xl border border-gray-200 p-4 shadow-sm"
          >
            <time
              dateTime={item.timestamp}
              className="mb-3 block text-xs font-medium uppercase tracking-wide text-genera-roxo/50"
            >
              {formatarData(item.timestamp)}
            </time>
            <div className="space-y-3">
              <MessageBubble remetente="paciente" texto={item.pergunta} />
              <MessageBubble
                remetente="ia"
                texto={item.resposta}
                fontes={item.fontes}
              />
            </div>
          </li>
        ))}
      </ol>

      {totalPaginas > 1 && (
        <nav
          aria-label="Paginação do histórico"
          className="mt-6 flex items-center justify-center gap-4"
        >
          <button
            type="button"
            onClick={() => setPagina((p) => Math.max(1, p - 1))}
            disabled={paginaAtual === 1}
            className="rounded-lg border border-gray-300 px-4 py-2 text-sm font-medium text-genera-roxo transition-colors hover:bg-genera-roxo/10 disabled:cursor-not-allowed disabled:opacity-40 focus:outline-none focus-visible:ring-2 focus-visible:ring-genera-magenta focus-visible:ring-offset-2"
          >
            Anterior
          </button>
          <span className="text-sm text-genera-roxo/70" aria-live="polite">
            Página {paginaAtual} de {totalPaginas}
          </span>
          <button
            type="button"
            onClick={() => setPagina((p) => Math.min(totalPaginas, p + 1))}
            disabled={paginaAtual === totalPaginas}
            className="rounded-lg border border-gray-300 px-4 py-2 text-sm font-medium text-genera-roxo transition-colors hover:bg-genera-roxo/10 disabled:cursor-not-allowed disabled:opacity-40 focus:outline-none focus-visible:ring-2 focus-visible:ring-genera-magenta focus-visible:ring-offset-2"
          >
            Próxima
          </button>
        </nav>
      )}
    </div>
  );
}
