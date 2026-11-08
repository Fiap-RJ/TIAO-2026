import type { Classificacao, EstadoDispositivo } from '../api/types'
import { formatarPercentual, ROTULO_ESTADO, ROTULO_FAIXA } from '../lib/format'

/** Selo de faixa: cor + texto, para não depender só da cor. */
export function SeloRisco({ classificacao }: { classificacao: Classificacao | null }) {
  if (!classificacao) return <span className="chip chip-neutro">Sem avaliação</span>
  return (
    <span className={`chip chip-${classificacao.toLowerCase()}`}>{ROTULO_FAIXA[classificacao]}</span>
  )
}

export function SeloEstado({ estado }: { estado: EstadoDispositivo }) {
  const classe = { normal: 'baixo', atencao: 'moderado', critico: 'alto' }[estado]
  return (
    <span className={`chip chip-${classe}`}>
      <span className="ponto" aria-hidden="true" />
      Dispositivo: {ROTULO_ESTADO[estado]}
    </span>
  )
}

const FAIXAS: { de: number; ate: number; classe: string }[] = [
  { de: 0, ate: 0.4, classe: 'baixo' },
  { de: 0.4, ate: 0.7, classe: 'moderado' },
  { de: 0.7, ate: 1, classe: 'alto' },
]

/** Medidor semicircular da probabilidade, com as faixas 0,40 e 0,70 da Fase 6. */
export function MedidorRisco({
  probabilidade,
  classificacao,
}: {
  probabilidade: number
  classificacao: Classificacao
}) {
  const raio = 80
  const cx = 100
  const cy = 95
  const ponto = (p: number) => {
    const angulo = Math.PI * (1 - p)
    return [cx + raio * Math.cos(angulo), cy - raio * Math.sin(angulo)] as const
  }
  const arco = (de: number, ate: number) => {
    const [x1, y1] = ponto(de)
    const [x2, y2] = ponto(ate)
    return `M ${x1} ${y1} A ${raio} ${raio} 0 0 1 ${x2} ${y2}`
  }
  const [px, py] = ponto(Math.min(Math.max(probabilidade, 0), 1))

  return (
    <figure className="medidor">
      <svg viewBox="0 0 200 110" role="img" aria-label={`Probabilidade de pico de risco ${formatarPercentual(probabilidade)}, ${ROTULO_FAIXA[classificacao]}`}>
        {FAIXAS.map(({ de, ate, classe }) => (
          <path key={classe} d={arco(de + 0.005, ate - 0.005)} className={`medidor-faixa medidor-${classe}`} />
        ))}
        <line x1={cx} y1={cy} x2={px} y2={py} className="medidor-ponteiro" />
        <circle cx={cx} cy={cy} r="5" className="medidor-centro" />
      </svg>
      <figcaption>
        <strong className={`texto-${classificacao.toLowerCase()}`}>{formatarPercentual(probabilidade)}</strong>
        <span>probabilidade de pico de risco</span>
      </figcaption>
    </figure>
  )
}
