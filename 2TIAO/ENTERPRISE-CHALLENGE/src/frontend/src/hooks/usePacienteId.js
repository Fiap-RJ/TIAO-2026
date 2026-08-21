/**
 * Centraliza o `paciente_id` que hoje está hardcoded no chat (`"uuid-123"`).
 * Enquanto não há autenticação/seleção de paciente, retorna um valor fixo —
 * mas concentrado em um único lugar, pronto para trocar por contexto/sessão.
 */
const PACIENTE_ID_FIXO = 'uuid-123';

export function usePacienteId() {
  return PACIENTE_ID_FIXO;
}
