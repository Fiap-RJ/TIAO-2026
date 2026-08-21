import { useId, useState } from 'react';
import { getRiskLevel } from './riskLevelMap';

/**
 * RiskCard — card de uma característica genética (A2).
 * Exibe característica, nível neutro e conclusão curta; o botão "ver detalhes"
 * expande a explicação detalhada e as recomendações.
 */
export default function RiskCard({ risco }) {
  const [aberto, setAberto] = useState(false);
  const detalhesId = useId();
  const { label, badgeClasses } = getRiskLevel(risco.categoria_impacto);

  return (
    <article className="rounded-xl border border-gray-200 bg-white p-4 shadow-sm">
      <div className="flex items-start justify-between gap-3">
        <h3 className="font-semibold text-genera-roxo">{risco.caracteristica}</h3>
        <span
          className={`shrink-0 rounded-full px-3 py-1 text-xs font-medium ${badgeClasses}`}
        >
          {label}
        </span>
      </div>

      <p className="mt-2 text-sm text-genera-roxo/80">{risco.conclusao_curta}</p>

      <button
        type="button"
        onClick={() => setAberto((v) => !v)}
        aria-expanded={aberto}
        aria-controls={detalhesId}
        className="mt-3 text-sm font-medium text-genera-magentahover underline-offset-2 hover:underline focus:outline-none focus-visible:ring-2 focus-visible:ring-genera-magenta focus-visible:ring-offset-2"
      >
        {aberto ? 'Ocultar detalhes' : 'Ver detalhes'}
      </button>

      {aberto && (
        <div id={detalhesId} className="mt-3 border-t border-gray-100 pt-3">
          <p className="text-sm leading-relaxed text-genera-roxo/80">
            {risco.explicacao_detalhada}
          </p>
          {risco.recomendacoes?.length > 0 && (
            <div className="mt-3">
              <h4 className="text-sm font-semibold text-genera-roxo">
                Recomendações
              </h4>
              <ul className="mt-1 list-disc space-y-1 pl-5 text-sm text-genera-roxo/80">
                {risco.recomendacoes.map((rec, i) => (
                  <li key={i}>{rec}</li>
                ))}
              </ul>
            </div>
          )}
        </div>
      )}
    </article>
  );
}
