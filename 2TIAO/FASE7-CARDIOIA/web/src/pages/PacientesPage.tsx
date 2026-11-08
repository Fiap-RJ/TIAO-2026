import { Link } from 'react-router-dom'
import { api } from '../api/client'
import type { Classificacao } from '../api/types'
import { SeloEstado, SeloRisco } from '../components/Risco'
import { usePolling } from '../hooks/usePolling'
import { formatarNumero, formatarPercentual, tempoRelativo } from '../lib/format'

const ORDEM: Record<Classificacao, number> = { ALTO: 0, MODERADO: 1, BAIXO: 2 }

export function PacientesPage() {
  const { dados, erro, carregando } = usePolling(api.listarPacientes, 10_000)

  // pacientes em risco maior aparecem primeiro
  const pacientes = [...(dados ?? [])].sort(
    (a, b) =>
      (a.classificacao ? ORDEM[a.classificacao] : 3) - (b.classificacao ? ORDEM[b.classificacao] : 3) ||
      (b.probabilidade ?? 0) - (a.probabilidade ?? 0),
  )

  return (
    <>
      <div className="cabecalho-pagina">
        <h2>Pacientes monitorados</h2>
        <p>Ordenados pelo risco de pico previsto. Atualiza a cada 10 s.</p>
      </div>

      {erro && (
        <p className="erro" role="alert">
          {erro}
        </p>
      )}
      {carregando && !dados && <p className="vazio">Carregando pacientes…</p>}
      {dados && pacientes.length === 0 && <p className="vazio">Nenhum paciente cadastrado.</p>}

      <ul className="lista-pacientes">
        {pacientes.map((p) => (
          <li key={p.id}>
            <Link to={`/pacientes/${p.id}`} className={`cartao paciente-item borda-${p.classificacao?.toLowerCase() ?? 'neutro'}`}>
              <div className="paciente-id">
                <strong>{p.nome}</strong>
                <span>
                  {p.idade} anos · {p.leito}
                </span>
              </div>
              <div className="paciente-sinais">
                {p.ultima_leitura ? (
                  <>
                    <span>
                      <b>{p.ultima_leitura.fc}</b> bpm
                    </span>
                    <span>
                      <b>{p.ultima_leitura.spo2}</b>% SpO₂
                    </span>
                    <span>
                      <b>{formatarNumero(p.ultima_leitura.temperatura)}</b> °C
                    </span>
                  </>
                ) : (
                  <span>Sem leituras</span>
                )}
              </div>
              <div className="paciente-risco">
                <SeloRisco classificacao={p.classificacao} />
                {p.probabilidade !== null && <span className="prob">{formatarPercentual(p.probabilidade)}</span>}
              </div>
              <div className="paciente-rodape">
                {p.ultima_leitura && <SeloEstado estado={p.ultima_leitura.estado} />}
                {p.ultima_leitura && <small>Última leitura {tempoRelativo(p.ultima_leitura.ts)}</small>}
              </div>
            </Link>
          </li>
        ))}
      </ul>
    </>
  )
}
