import { useEffect, useState } from 'react';
import { deleteHistorico, getHistorico } from '../services/api';
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
  const [apagando, setApagando] = useState(false);
  const [erroExclusao, setErroExclusao] = useState(false);

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

  // Direito de exclusão (LGPD): apaga histórico e laudo enviado do paciente.
  const apagarDados = async () => {
    const confirmado = window.confirm(
      'Isso vai apagar de forma permanente todo o seu histórico de conversas e o laudo que você enviou. Essa ação não pode ser desfeita. Deseja continuar?',
    );
    if (!confirmado) return;

    setApagando(true);
    setErroExclusao(false);
    try {
      await deleteHistorico(pacienteId);
      recarregar();
    } catch {
      setErroExclusao(true);
    } finally {
      setApagando(false);
    }
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

      {!carregando && !erro && (
        <div className="mt-8 border-t border-gray-200 pt-6">
          <p className="max-w-2xl text-sm text-genera-roxo/70">
            Você pode apagar a qualquer momento seu histórico de conversas e o
            laudo enviado.
          </p>
          <button
            type="button"
            onClick={apagarDados}
            disabled={apagando}
            className="mt-3 rounded-lg border border-genera-magentahover px-4 py-2 text-sm font-medium text-genera-magentahover transition-colors hover:bg-pink-50 disabled:cursor-not-allowed disabled:opacity-40 focus:outline-none focus-visible:ring-2 focus-visible:ring-genera-magenta focus-visible:ring-offset-2"
          >
            {apagando ? 'Apagando...' : 'Apagar meus dados'}
          </button>
          {erroExclusao && (
            <p role="alert" className="mt-2 text-sm text-genera-magentahover">
              Não foi possível apagar seus dados agora. Tente novamente mais
              tarde.
            </p>
          )}
        </div>
      )}
    </section>
  );
}
