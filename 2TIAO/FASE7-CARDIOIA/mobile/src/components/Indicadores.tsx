import { StyleSheet, Text, View } from 'react-native'
import Svg, { Circle, Line, Path, Polyline } from 'react-native-svg'
import type { Classificacao, EstadoDispositivo } from '../api/types'
import { formatarPercentual, ROTULO_ESTADO, ROTULO_FAIXA } from '../lib/format'
import { cores, corEstado, corFaixa } from '../theme'

/** Selo de faixa: cor + texto, para não depender só da cor. */
export function SeloRisco({ classificacao }: { classificacao: Classificacao | null }) {
  const estilo = classificacao ? corFaixa[classificacao] : { cor: cores.textoSuave, fundo: cores.superficie2 }
  return (
    <View style={[estilos.selo, { backgroundColor: estilo.fundo }]}>
      <Text style={[estilos.seloTexto, { color: estilo.cor }]}>
        {classificacao ? ROTULO_FAIXA[classificacao] : 'Sem avaliação'}
      </Text>
    </View>
  )
}

export function SeloEstado({ estado }: { estado: EstadoDispositivo }) {
  const { cor, fundo } = corEstado[estado]
  return (
    <View style={[estilos.selo, { backgroundColor: fundo }]}>
      <View style={[estilos.ponto, { backgroundColor: cor }]} />
      <Text style={[estilos.seloTexto, { color: cor }]}>Dispositivo: {ROTULO_ESTADO[estado]}</Text>
    </View>
  )
}

const FAIXAS = [
  { de: 0, ate: 0.4, cor: cores.baixo },
  { de: 0.4, ate: 0.7, cor: cores.moderado },
  { de: 0.7, ate: 1, cor: cores.alto },
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
    <View
      style={estilos.medidor}
      accessible
      accessibilityLabel={`Probabilidade de pico de risco ${formatarPercentual(probabilidade)}, ${ROTULO_FAIXA[classificacao]}`}
    >
      <Svg width={200} height={110} viewBox="0 0 200 110">
        {FAIXAS.map((f) => (
          <Path key={f.cor} d={arco(f.de + 0.005, f.ate - 0.005)} stroke={f.cor} strokeWidth={16} fill="none" />
        ))}
        <Line x1={cx} y1={cy} x2={px} y2={py} stroke={cores.texto} strokeWidth={3} strokeLinecap="round" />
        <Circle cx={cx} cy={cy} r={5} fill={cores.texto} />
      </Svg>
      <Text style={[estilos.medidorValor, { color: corFaixa[classificacao].cor }]}>
        {formatarPercentual(probabilidade)}
      </Text>
      <Text style={estilos.medidorLegenda}>probabilidade de pico de risco</Text>
    </View>
  )
}

/** Linha simples das últimas leituras, com uma linha tracejada no limiar de risco. */
export function Tendencia({
  valores,
  limiar,
  min,
  max,
  largura,
}: {
  valores: number[]
  limiar: number
  min: number
  max: number
  largura: number
}) {
  const altura = 56
  if (valores.length < 2 || largura <= 0) return <View style={{ height: altura }} />
  const y = (v: number) => altura - ((Math.min(Math.max(v, min), max) - min) / (max - min)) * altura
  const passo = largura / (valores.length - 1)
  const pontos = valores.map((v, i) => `${i * passo},${y(v)}`).join(' ')
  return (
    <Svg width={largura} height={altura}>
      <Line x1={0} x2={largura} y1={y(limiar)} y2={y(limiar)} stroke={cores.alto} strokeDasharray="4 4" strokeOpacity={0.6} />
      <Polyline points={pontos} fill="none" stroke={cores.marca} strokeWidth={2} />
    </Svg>
  )
}

const estilos = StyleSheet.create({
  selo: {
    flexDirection: 'row',
    alignItems: 'center',
    alignSelf: 'flex-start',
    gap: 6,
    paddingHorizontal: 10,
    paddingVertical: 4,
    borderRadius: 999,
  },
  seloTexto: { fontSize: 12, fontWeight: '700' },
  ponto: { width: 8, height: 8, borderRadius: 4 },
  medidor: { alignItems: 'center' },
  medidorValor: { fontSize: 32, fontWeight: '800', marginTop: -10 },
  medidorLegenda: { fontSize: 12, color: cores.textoSuave },
})
