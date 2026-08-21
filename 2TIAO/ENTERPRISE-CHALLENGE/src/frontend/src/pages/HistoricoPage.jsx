import { useEffect, useState } from 'react';
import { getHistorico } from '../services/api';
import { usePacienteId } from '../hooks/usePacienteId';
import HistoryList from '../components/historico/HistoryList';
import LoadingState from '../components/feedback/LoadingState';
import ErrorState from '../components/feedback/ErrorState';
import EmptyState from '../components/feedback/EmptyState';

/** HistoricoPage — histórico de interações do paciente com o agente (A4). */
export default function HistoricoPage() {
  const pacienteId = usePacienteId();
  const [itens, setItens] = useState([]);
  const [carregando, setCarregando] = useState(true);
  const [erro, setErro] = useState(null);
  const [tentativa, setTentativa] = useState(0);

  useEffect(() => {
    let ativo = true;
    async function carregar() {
      try {
        const dados = await getHistorico(pacienteId);
        if (ativo) setItens(dados);
      } catch (e) {
        if (ativo) setErro(e);
      } finally {
        if (ativo) setCarregando(false);
      }
    }
    carregar();
    return () => {
      ativo = false;
    };
  }, [pacienteId, tentativa]);

  const recarregar = () => {
    setErro(null);
    setCarregando(true);
    setTentativa((t) => t + 1);
  };

  return (
    <section>
      <h1 className="text-2xl font-bold text-genera-roxo">
        Histórico de interações
      </h1>
      <p className="mt-2 max-w-2xl text-genera-roxo/70">
        Suas conversas anteriores com o assistente, da mais recente para a mais
        antiga.
      </p>

      {carregando && <LoadingState mensagem="Carregando seu histórico..." />}

      {erro && !carregando && (
        <ErrorState
          mensagem="Não foi possível carregar o histórico agora. Tente novamente mais tarde."
          onRetry={recarregar}
        />
      )}

      {!carregando && !erro && itens.length === 0 && (
        <EmptyState mensagem="Você ainda não tem interações registradas. Converse com o assistente na aba Chat para começar." />
      )}

      {!carregando && !erro && itens.length > 0 && (
        <div className="mt-6">
          <HistoryList itens={itens} />
        </div>
      )}
    </section>
  );
}
