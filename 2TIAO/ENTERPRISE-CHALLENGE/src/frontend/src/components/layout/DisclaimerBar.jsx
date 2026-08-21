/**
 * Aviso fixo de governança exibido em todas as telas do dashboard.
 * Reaproveita o texto de segurança que hoje vive no rodapé do App.jsx (chat).
 */
export default function DisclaimerBar() {
  return (
    <footer
      role="contentinfo"
      className="border-t border-gray-200 bg-genera-roxo/5 px-4 py-3 text-center"
    >
      <p className="mx-auto max-w-3xl text-xs leading-relaxed text-genera-roxo/70">
        <span className="font-semibold">Aviso de Segurança e Governança:</span>{' '}
        Este assistente utiliza IA generativa para a estruturação de laudos. As
        informações apresentadas não substituem um diagnóstico médico ou a
        avaliação de um profissional de saúde.
      </p>
    </footer>
  );
}
