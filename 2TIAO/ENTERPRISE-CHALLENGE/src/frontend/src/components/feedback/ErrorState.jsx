/**
 * ErrorState — feedback de erro reutilizável (A6).
 * `role="alert"` para anunciar o erro imediatamente. Aceita um `onRetry`
 * opcional para permitir nova tentativa sem recarregar a página.
 */
export default function ErrorState({
  mensagem = 'Não foi possível carregar os dados agora. Tente novamente mais tarde.',
  onRetry,
}) {
  return (
    <div
      role="alert"
      className="mt-6 rounded-lg border border-amber-200 bg-amber-50 px-4 py-4 text-amber-800"
    >
      <p>{mensagem}</p>
      {onRetry && (
        <button
          type="button"
          onClick={onRetry}
          className="mt-3 rounded-lg border border-amber-300 px-4 py-2 text-sm font-medium transition-colors hover:bg-amber-100 focus:outline-none focus-visible:ring-2 focus-visible:ring-genera-magenta focus-visible:ring-offset-2"
        >
          Tentar novamente
        </button>
      )}
    </div>
  );
}
