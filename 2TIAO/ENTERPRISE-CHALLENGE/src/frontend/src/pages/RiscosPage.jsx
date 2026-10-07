import { useEffect, useState } from 'react';
import { getRiscos } from '../services/api';
import { usePacienteId } from '../hooks/usePacienteId';
import RiskCard from '../components/risco/RiskCard';
import { getRiskLevelPorNivel } from '../components/risco/riskLevelMap';
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

const formatarPercentual = (valor) =>
  `${Number(valor).toLocaleString('pt-BR', { maximumFractionDigits: 2 })}%`;

/** Seção "Escala de risco genético": risco poligênico estimado por doença. */
function EscalaRiscoGenetico({ escala }) {
  return (
    <div className="mt-10">
      <h2 className="text-lg font-semibold text-genera-roxo">
        Escala de risco genético
      </h2>
      <p
        role="note"
        className="mt-2 max-w-2xl text-sm text-genera-roxo/70"
      >
        Risco poligênico: vários genes somam pequenos efeitos e indicam uma
        tendência estatística em relação à população, não uma certeza. Um
        risco aumentado não significa que você vai desenvolver a condição.
      </p>
      <ul className="mt-4 grid gap-4 sm:grid-cols-2">
        {escala.map((item) => {
          const { label, badgeClasses } = getRiskLevelPorNivel(item.nivel);
          return (
            <li
              key={item.doenca}
              className="rounded-xl border border-gray-200 bg-white p-4 shadow-sm"
            >
              <div className="flex items-start justify-between gap-3">
                <h3 className="font-semibold text-genera-roxo">
                  {item.doenca}
                </h3>
                <span
                  className={`shrink-0 rounded-full px-3 py-1 text-xs font-medium ${badgeClasses}`}
                >
                  {label}
                </span>
              </div>
              <p className="mt-2 text-sm text-genera-roxo/80">
                Risco estimado:{' '}
                <span className="font-semibold">
                  {formatarPercentual(item.risco_calculado_percentual)}
                </span>
              </p>
              <p className="text-sm text-genera-roxo/70">
                Intervalo de referência:{' '}
                {formatarPercentual(item.intervalo_minimo)} a{' '}
                {formatarPercentual(item.intervalo_maximo)}
              </p>
            </li>
          );
        })}
      </ul>
    </div>
  );
}

/** RiscosPage — cards de risco agrupados por painel + escala de risco (A2). */
export default function RiscosPage() {
  const pacienteId = usePacienteId();
  const [riscos, setRiscos] = useState([]);
  const [escala, setEscala] = useState([]);
  const [carregando, setCarregando] = useState(true);
  const [erro, setErro] = useState(null);
  const [tentativa, setTentativa] = useState(0);

  useEffect(() => {
    let ativo = true;
    async function carregar() {
      try {
        const dados = await getRiscos(pacienteId);
        if (ativo) {
          setRiscos(dados.riscos);
          setEscala(dados.escala);
        }
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
  const semDados = grupos.length === 0 && escala.length === 0;

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

      {!carregando && !erro && semDados && (
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

      {!carregando && !erro && escala.length > 0 && (
        <EscalaRiscoGenetico escala={escala} />
      )}
    </section>
  );
}
