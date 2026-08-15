import { useEffect, useState } from 'react';
import { getRiscos } from '../services/api';
import { usePacienteId } from '../hooks/usePacienteId';
import RiskCard from '../components/risco/RiskCard';
import LoadingState from '../components/feedback/LoadingState';
import ErrorState from '../components/feedback/ErrorState';
import EmptyState from '../components/feedback/EmptyState';

/** Agrupa a lista achatada de riscos por painel, preservando a ordem de chegada. */
function agruparPorPainel(riscos) {
  const grupos = new Map();
  for (const risco of riscos) {
    if (!grupos.has(risco.painel)) grupos.set(risco.painel, []);
    grupos.get(risco.painel).push(risco);
  }
  return [...grupos.entries()].map(([painel, itens]) => ({ painel, itens }));
}

/** RiscosPage — cards de risco agrupados por painel (A2). */
export default function RiscosPage() {
  const pacienteId = usePacienteId();
  const [riscos, setRiscos] = useState([]);
  const [carregando, setCarregando] = useState(true);
  const [erro, setErro] = useState(null);
  const [tentativa, setTentativa] = useState(0);

  useEffect(() => {
    let ativo = true;
    async function carregar() {
      try {
        const dados = await getRiscos(pacienteId);
        if (ativo) setRiscos(dados);
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

  const grupos = agruparPorPainel(riscos);

  return (
    <section>
      <h1 className="text-2xl font-bold text-genera-roxo">
        Riscos e predisposições
      </h1>
      <p className="mt-2 max-w-2xl text-genera-roxo/70">
        Seus resultados por painel genético. As classificações usam uma escala
        neutra (baixo, moderado, atenção) e não representam diagnóstico.
      </p>

      {carregando && <LoadingState mensagem="Carregando seus resultados..." />}

      {erro && !carregando && (
        <ErrorState
          mensagem="Não foi possível carregar os riscos agora. Tente novamente mais tarde."
          onRetry={recarregar}
        />
      )}

      {!carregando && !erro && grupos.length === 0 && (
        <EmptyState mensagem="Nenhum resultado disponível no momento." />
      )}

      {!carregando && !erro && grupos.length > 0 && (
        <div className="mt-6 space-y-8">
          {grupos.map(({ painel, itens }) => (
            <div key={painel}>
              <h2 className="mb-3 text-lg font-semibold text-genera-roxo">
                {painel}
              </h2>
              <div className="grid gap-4 sm:grid-cols-2">
                {itens.map((risco, i) => (
                  <RiskCard key={`${painel}-${i}`} risco={risco} />
                ))}
              </div>
            </div>
          ))}
        </div>
      )}
    </section>
  );
}
