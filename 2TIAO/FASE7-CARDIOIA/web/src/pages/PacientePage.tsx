import { useCallback, useState } from 'react'
import { Link, useParams } from 'react-router-dom'
import { api, ApiError } from '../api/client'
import type { Leitura, RespostaAtendimento } from '../api/types'
import { useAuth } from '../auth/useAuth'
import { Chat } from '../components/Chat'
import { GraficoSinais } from '../components/GraficoSinais'
import { MedidorRisco, SeloEstado, SeloRisco } from '../components/Risco'
import { usePolling } from '../hooks/usePolling'
import {
  formatarHora,
  formatarNumero,
  ROTULO_ORIGEM,
  ROTULO_VARIAVEL,
  tempoRelativo,
  UNIDADE_VARIAVEL,
} from '../lib/format'

export function PacientePage() {
  const { id = '' } = useParams()
  const { usuario } = useAuth()
  const carregar = useCallback(() => api.obterStatus(id), [id])
  const { dados, erro, carregando, atualizadoEm, recarregar } = usePolling(carregar, 5_000)
  const [reavaliando, setReavaliando] = useState(false)
  const [erroAvaliacao, setErroAvaliacao] = useState<string | null>(null)

  async function reavaliar() {
    setReavaliando(true)
    setErroAvaliacao(null)
    try {
      await api.avaliar(id)
      await recarregar()
    } catch (e) {
      setErroAvaliacao(e instanceof ApiError ? e.message : 'Falha ao reavaliar o risco.')
    } finally {
      setReavaliando(false)
    }
  }

  if (carregando && !dados) return <p className="vazio">Carregando painel do paciente…</p>
  if (!dados) {
    return (
      <p className="erro" role="alert">
        {erro ?? 'Paciente não encontrado.'}
      </p>
    )
  }

  const { paciente, leituras, avaliacao } = dados
  const ultima = leituras.at(-1)
  const ehMedico = usuario?.perfil === 'medico'

  return (
    <>
      {ehMedico && (
        <Link to="/pacientes" className="voltar">
          ← Pacientes
        </Link>
      )}
      <div className="cabecalho-pagina cabecalho-paciente">
        <div>
          <h2>{paciente.nome}</h2>
          <p>
            {paciente.idade} anos · {paciente.leito}
          </p>
        </div>
        <div className="cabecalho-status">
          {ultima && <SeloEstado estado={ultima.estado} />}
          <small aria-live="polite">
            {erro ? `Falha na atualização: ${erro}` : atualizadoEm ? `Atualizado às ${formatarHora(atualizadoEm)}` : ''}
          </small>
        </div>
      </div>

      <div className="painel">
        <div className="painel-principal">
          <section className="cartao risco" aria-labelledby="titulo-risco">
            <div className="cartao-titulo">
              <h3 id="titulo-risco">Risco de pico previsto</h3>
              {ehMedico && (
                <button type="button" className="botao botao-secundario" onClick={reavaliar} disabled={reavaliando}>
                  {reavaliando ? 'Reavaliando…' : 'Reavaliar agora'}
                </button>
              )}
            </div>
            {erroAvaliacao && (
              <p className="erro" role="alert">
                {erroAvaliacao}
              </p>
            )}
            {avaliacao ? <ResumoRisco avaliacao={avaliacao} /> : <p className="vazio">Ainda sem avaliação de risco.</p>}
          </section>

          <section className="cartao" aria-labelledby="titulo-sinais">
            <div className="cartao-titulo">
              <h3 id="titulo-sinais">Sinais vitais em tempo real</h3>
              {ultima && <small>Última leitura {tempoRelativo(ultima.ts)}</small>}
            </div>
            {ultima && <SinaisAtuais leitura={ultima} />}
            <GraficoSinais leituras={leituras} />
          </section>

          {avaliacao && <Recomendacao avaliacao={avaliacao} ehMedico={ehMedico} />}
        </div>

        <aside className="painel-lateral">
          <Chat pacienteId={paciente.id} />
        </aside>
      </div>

      <p className="aviso-legal">{avaliacao?.aviso_legal ?? AVISO_PADRAO}</p>
    </>
  )
}

const AVISO_PADRAO =
  'Aviso: o CardioIA é um sistema acadêmico e informativo. Não realiza diagnóstico, não prescreve ' +
  'tratamentos e não substitui a avaliação de um profissional de saúde.'

function ResumoRisco({ avaliacao }: { avaliacao: RespostaAtendimento }) {
  const { avaliacao_risco: r } = avaliacao
  return (
    <div className="risco-corpo">
      <MedidorRisco probabilidade={r.probabilidade} classificacao={r.classificacao} />
      <dl className="risco-detalhes">
        <div>
          <dt>Classificação</dt>
          <dd>
            <SeloRisco classificacao={r.classificacao} />
          </dd>
        </div>
        <div>
          <dt>Pico previsto</dt>
          <dd>{r.pico_risco_previsto ? 'Sim' : 'Não'}</dd>
        </div>
        <div>
          <dt>Protocolos acionados</dt>
          <dd>{avaliacao.protocolos.length}</dd>
        </div>
        <div>
          <dt>Avaliado</dt>
          <dd>{tempoRelativo(avaliacao.gerado_em)}</dd>
        </div>
      </dl>
      {r.avisos.length > 0 && (
        <ul className="avisos">
          {r.avisos.map((a) => (
            <li key={a}>{a}</li>
          ))}
        </ul>
      )}
    </div>
  )
}

function SinaisAtuais({ leitura }: { leitura: Leitura }) {
  const itens = [
    { rotulo: 'Frequência cardíaca', valor: leitura.fc, unidade: 'bpm', alerta: leitura.fc > 110 },
    { rotulo: 'SpO₂', valor: leitura.spo2, unidade: '%', alerta: leitura.spo2 < 92 },
    { rotulo: 'Temperatura', valor: leitura.temperatura, unidade: '°C', alerta: leitura.temperatura > 38 },
  ]
  return (
    <div className="sinais">
      {itens.map((i) => (
        <div key={i.rotulo} className={`sinal ${i.alerta ? 'sinal-alerta' : ''}`}>
          <span>{i.rotulo}</span>
          <strong>
            {formatarNumero(i.valor)}
            <small> {i.unidade}</small>
          </strong>
          {i.alerta && <em>acima do limiar de risco</em>}
        </div>
      ))}
    </div>
  )
}

function Recomendacao({ avaliacao, ehMedico }: { avaliacao: RespostaAtendimento; ehMedico: boolean }) {
  return (
    <section className="cartao" aria-labelledby="titulo-recomendacao">
      <div className="cartao-titulo">
        <h3 id="titulo-recomendacao">Recomendação</h3>
        <small>
          Origem: {ROTULO_ORIGEM[avaliacao.origem]}
          {avaliacao.motivo_fallback ? ` (${avaliacao.motivo_fallback})` : ''}
        </small>
      </div>

      <p className="explicacao">{avaliacao.explicacao}</p>

      <div className="colunas">
        <div>
          <h4>Protocolos acionados</h4>
          {avaliacao.protocolos.length === 0 ? (
            <p className="vazio">Nenhum protocolo acionado.</p>
          ) : (
            <ul className="protocolos">
              {avaliacao.protocolos.map((p) => (
                <li key={p.id}>
                  <span className="protocolo-id">{p.id}</span>
                  <div>
                    <p>{p.texto}</p>
                    <small>{p.justificativa}</small>
                  </div>
                </li>
              ))}
            </ul>
          )}

          {avaliacao.sinais_de_atencao.length > 0 && (
            <>
              <h4>Sinais de atenção</h4>
              <ul className="sinais-atencao">
                {avaliacao.sinais_de_atencao.map((s) => (
                  <li key={s.variavel}>
                    <b>{ROTULO_VARIAVEL[s.variavel] ?? s.variavel}</b> em {formatarNumero(s.valor)}: acima do limiar
                    de risco ({formatarNumero(s.limiar_risco)}), o {s.protocolo_id} aciona em{' '}
                    {formatarNumero(s.limiar_protocolo)}.
                  </li>
                ))}
              </ul>
            </>
          )}
        </div>

        <div>
          <h4>Ações operacionais</h4>
          <ol className="acoes">
            {avaliacao.acoes_operacionais.map((a) => (
              <li key={a}>{a}</li>
            ))}
          </ol>
        </div>
      </div>

      {ehMedico && (
        <details className="indicadores">
          <summary>Indicadores usados pelo modelo</summary>
          <dl>
            {Object.entries(avaliacao.paciente).map(([chave, valor]) => (
              <div key={chave}>
                <dt>{ROTULO_VARIAVEL[chave] ?? chave}</dt>
                <dd>
                  {formatarNumero(valor)} {UNIDADE_VARIAVEL[chave] ?? ''}
                </dd>
              </div>
            ))}
          </dl>
          {avaliacao.cadeia_agentes.length > 0 && (
            <p className="cadeia">Agentes: {avaliacao.cadeia_agentes.join(' → ')}</p>
          )}
        </details>
      )}
    </section>
  )
}
