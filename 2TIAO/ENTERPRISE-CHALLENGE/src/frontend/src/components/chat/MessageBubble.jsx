/**
 * MessageBubble — bolha de mensagem reutilizável pelo chat (A5) e pelo
 * histórico (A4), para consistência visual.
 *
 * Props:
 *  - remetente: 'paciente' | 'ia'
 *  - texto: string (quebras de linha preservadas)
 *  - fontes: [{ painel, marcador, gene }] (opcional)
 *  - painelUtilizado: painel especialista que respondeu (opcional)
 *  - guardrailsAcionados: string[] — se não vazio, mostra aviso discreto (opcional)
 *  - onPedirDetalhes: se informado, mostra o botão "Quero mais detalhes" (opcional)
 *  - desabilitarDetalhes: desabilita o botão (ex.: enquanto há requisição em curso)
 */
export default function MessageBubble({
  remetente,
  texto,
  fontes = [],
  painelUtilizado,
  guardrailsAcionados = [],
  onPedirDetalhes,
  desabilitarDetalhes = false,
}) {
  const doPaciente = remetente === 'paciente';

  return (
    <div className={doPaciente ? 'text-right' : 'text-left'}>
      <div
        className={`inline-block max-w-[80%] rounded-2xl p-4 shadow-sm ${doPaciente
          ? 'rounded-br-none bg-genera-roxo text-white'
          : 'rounded-bl-none border border-gray-200 bg-white text-genera-roxo'
          }`}
      >
        {painelUtilizado && (
          <p className="mb-2 text-left text-xs font-medium uppercase tracking-wide text-genera-roxo/60">
            Painel: {painelUtilizado}
          </p>
        )}
        <p className="whitespace-pre-line leading-relaxed">{texto}</p>
        {guardrailsAcionados && guardrailsAcionados.length > 0 && (
          <p className="mt-2 text-left text-xs italic text-genera-roxo/60">
            Resposta ajustada pelas salvaguardas
          </p>
        )}
        {fontes && fontes.length > 0 && (
          <div className="mt-3 border-t border-current/20 pt-3 text-left text-xs opacity-80">
            <span className="font-bold">Fontes do laudo: </span>
            {fontes.map((fonte, i) => (
              <span
                key={i}
                className="mb-1 mr-1 inline-block rounded bg-gray-100 px-2 py-0.5 text-genera-roxo"
              >
                {fonte.painel} — {fonte.marcador} ({fonte.gene})
              </span>
            ))}
          </div>
        )}
        {onPedirDetalhes && (
          <div className="mt-3 text-left">
            <button
              type="button"
              onClick={onPedirDetalhes}
              disabled={desabilitarDetalhes}
              className="rounded-full border border-genera-magentahover px-4 py-1.5 text-sm font-medium text-genera-magentahover transition-colors hover:bg-pink-50 disabled:cursor-not-allowed disabled:opacity-40 focus:outline-none focus-visible:ring-2 focus-visible:ring-genera-magenta focus-visible:ring-offset-2"
            >
              Quero mais detalhes
            </button>
          </div>
        )}
      </div>
    </div>
  );
}
