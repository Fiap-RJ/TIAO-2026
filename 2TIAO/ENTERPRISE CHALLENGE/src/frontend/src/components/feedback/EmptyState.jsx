/**
 * EmptyState — feedback de "sem dados" reutilizável (A6).
 */
export default function EmptyState({ mensagem = 'Nada por aqui ainda.' }) {
  return (
    <p className="mt-6 rounded-lg border border-dashed border-gray-300 px-4 py-6 text-center text-genera-roxo/70">
      {mensagem}
    </p>
  );
}
