import { useEffect, useState } from 'react';
import { getAncestralidade } from '../services/api';
import { usePacienteId } from '../hooks/usePacienteId';
import AncestryChart from '../components/ancestralidade/AncestryChart';
import LoadingState from '../components/feedback/LoadingState';
import ErrorState from '../components/feedback/ErrorState';
import EmptyState from '../components/feedback/EmptyState';

/** AncestralidadePage — resumo de ancestralidade (A3). */
export default function AncestralidadePage() {
  const pacienteId = usePacienteId();
  const [dados, setDados] = useState(null);
  const [carregando, setCarregando] = useState(true);
  const [erro, setErro] = useState(null);
  const [tentativa, setTentativa] = useState(0);

  useEffect(() => {
    let ativo = true;
    async function carregar() {
      try {
        const resposta = await getAncestralidade(pacienteId);
        if (ativo) setDados(resposta);
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

  const componentes = dados?.componentes ?? [];

  return (
    <section>
      <h1 className="text-2xl font-bold text-genera-roxo">
        Resumo de ancestralidade
      </h1>
      <p className="mt-2 max-w-2xl text-genera-roxo/70">
        Estimativa da composição de ancestralidade a partir do seu perfil
        genético.
      </p>

      {/* Aviso: enquanto a fonte estruturada não expõe ancestralidade (ver
          seção 2 do spec), o dado exibido é fictício, só para demonstração. */}
      {dados?.ilustrativo && (
        <p
          role="note"
          className="mt-4 rounded-lg border border-amber-200 bg-amber-50 px-4 py-3 text-sm text-amber-800"
        >
          <span className="font-semibold">Dados ilustrativos:</span> o relatório
          atual ainda não fornece dados de ancestralidade. Os valores abaixo são
          fictícios e servem apenas para demonstrar a visualização.
        </p>
      )}

      {carregando && (
        <LoadingState mensagem="Carregando composição de ancestralidade..." />
      )}

      {erro && !carregando && (
        <ErrorState
          mensagem="Não foi possível carregar a ancestralidade agora. Tente novamente mais tarde."
          onRetry={recarregar}
        />
      )}

      {!carregando && !erro && componentes.length === 0 && (
        <EmptyState mensagem="Nenhum dado de ancestralidade disponível no momento." />
      )}

      {!carregando && !erro && componentes.length > 0 && (
        <div className="mt-6 rounded-xl border border-gray-200 p-4 shadow-sm">
          <AncestryChart componentes={componentes} />
        </div>
      )}
    </section>
  );
}
