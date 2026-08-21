/**
 * MessageBubble — bolha de mensagem reutilizável pelo chat (A5) e pelo
 * histórico (A4), para consistência visual.
 *
 * Props:
 *  - remetente: 'paciente' | 'ia'
 *  - texto: string
 *  - fontes: [{ painel, marcador, gene }] (opcional)
 */
export default function MessageBubble({ remetente, texto, fontes = [] }) {
  const doPaciente = remetente === 'paciente';

  return (
    <div className={doPaciente ? 'text-right' : 'text-left'}>
      <div
        className={`inline-block max-w-[80%] rounded-2xl p-4 shadow-sm ${
          doPaciente
            ? 'rounded-br-none bg-genera-roxo text-white'
            : 'rounded-bl-none border border-gray-200 bg-white text-genera-roxo'
        }`}
      >
        <p className="leading-relaxed">{texto}</p>
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
      </div>
    </div>
  );
}
