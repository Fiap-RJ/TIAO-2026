import {
  CartesianGrid,
  Line,
  LineChart,
  ReferenceLine,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from 'recharts'
import type { Leitura } from '../api/types'
import { formatarHora } from '../lib/format'

interface Serie {
  chave: 'fc' | 'spo2' | 'temperatura'
  titulo: string
  unidade: string
  dominio: [number | 'auto', number | 'auto']
  /** Limiares de risco e de protocolo da Fase 6, desenhados como linhas tracejadas. */
  limites: number[]
}

const SERIES: Serie[] = [
  { chave: 'fc', titulo: 'Frequência cardíaca', unidade: 'bpm', dominio: [40, 160], limites: [110, 120] },
  { chave: 'spo2', titulo: 'SpO₂', unidade: '%', dominio: [80, 100], limites: [92, 88] },
  { chave: 'temperatura', titulo: 'Temperatura', unidade: '°C', dominio: [35, 40], limites: [38] },
]

export function GraficoSinais({ leituras }: { leituras: Leitura[] }) {
  if (leituras.length === 0) {
    return <p className="vazio">Aguardando a primeira leitura do dispositivo.</p>
  }
  const dados = leituras.map((l) => ({ ...l, hora: formatarHora(l.ts) }))

  return (
    <div className="graficos">
      {SERIES.map((serie) => (
        <div key={serie.chave} className="grafico">
          <h4>
            {serie.titulo} <small>({serie.unidade})</small>
          </h4>
          <ResponsiveContainer width="100%" height={140}>
            <LineChart data={dados} margin={{ top: 6, right: 8, bottom: 0, left: -18 }}>
              <CartesianGrid vertical={false} stroke="var(--grade)" />
              <XAxis dataKey="hora" tick={{ fontSize: 11, fill: 'var(--texto-suave)' }} minTickGap={40} tickLine={false} axisLine={false} />
              <YAxis domain={serie.dominio} tick={{ fontSize: 11, fill: 'var(--texto-suave)' }} tickLine={false} axisLine={false} width={44} />
              {serie.limites.map((limite) => (
                <ReferenceLine key={limite} y={limite} stroke="var(--alto)" strokeDasharray="4 4" strokeOpacity={0.6} />
              ))}
              <Tooltip
                formatter={(valor) => [`${valor} ${serie.unidade}`, serie.titulo]}
                labelFormatter={(rotulo) => `às ${rotulo}`}
                contentStyle={{ background: 'var(--superficie)', border: '1px solid var(--borda)', borderRadius: 8 }}
              />
              <Line
                type="monotone"
                dataKey={serie.chave}
                stroke="var(--marca)"
                strokeWidth={2}
                dot={false}
                isAnimationActive={false}
              />
            </LineChart>
          </ResponsiveContainer>
        </div>
      ))}
    </div>
  )
}
