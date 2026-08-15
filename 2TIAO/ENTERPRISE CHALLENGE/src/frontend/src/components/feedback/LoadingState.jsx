/**
 * LoadingState — feedback de carregamento reutilizável (A6).
 * `role="status"` + aria-live para anunciar o carregamento a leitores de tela.
 */
export default function LoadingState({ mensagem = 'Carregando...' }) {
  return (
    <div
      role="status"
      aria-live="polite"
      className="mt-6 flex items-center gap-3 text-genera-roxo/60"
    >
      <span
        aria-hidden="true"
        className="h-4 w-4 animate-spin rounded-full border-2 border-genera-roxo/30 border-t-genera-magenta"
      />
      <span>{mensagem}</span>
    </div>
  );
}
