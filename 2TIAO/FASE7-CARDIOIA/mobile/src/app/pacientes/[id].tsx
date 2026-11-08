import { Redirect, router, Stack, useLocalSearchParams } from 'expo-router'
import { useCallback, useState } from 'react'
import { ActivityIndicator, Pressable, RefreshControl, ScrollView, StyleSheet, Text, View } from 'react-native'
import { api, ApiError } from '../../api/client'
import type { Leitura, RespostaAtendimento } from '../../api/types'
import { rotaInicial, useSessao } from '../../auth/sessao'
import { AvisoServidor } from '../../components/AvisoServidor'
import { MedidorRisco, SeloEstado, SeloRisco, Tendencia } from '../../components/Indicadores'
import { usePolling } from '../../hooks/usePolling'
import {
  formatarHora,
  formatarNumero,
  ROTULO_ORIGEM,
  ROTULO_VARIAVEL,
  tempoRelativo,
} from '../../lib/format'
import { base, cores } from '../../theme'

const AVISO_PADRAO =
  'Aviso: o CardioIA é um sistema acadêmico e informativo. Não realiza diagnóstico, não prescreve ' +
  'tratamentos e não substitui a avaliação de um profissional de saúde.'

export default function PainelPaciente() {
  const { id } = useLocalSearchParams<{ id: string }>()
  const { usuario } = useSessao()
  const carregar = useCallback(() => api.obterStatus(id), [id])
  const { dados, erro, carregando, atualizadoEm, recarregar } = usePolling(carregar, 5_000)
  const [reavaliando, setReavaliando] = useState(false)
  const [erroAvaliacao, setErroAvaliacao] = useState<string | null>(null)

  if (usuario?.perfil === 'paciente' && usuario.paciente_id !== id) {
    return <Redirect href={rotaInicial(usuario)} />
  }

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

  if (!dados) {
    return (
      <View style={[base.tela, estilos.centro]}>
        <AvisoServidor />
        {carregando ? <ActivityIndicator color={cores.marca} size="large" /> : <Text style={base.erro}>{erro}</Text>}
      </View>
    )
  }

  const { paciente, leituras, avaliacao } = dados
  const ultima = leituras.at(-1)
  const ehMedico = usuario?.perfil === 'medico'

  return (
    <View style={base.tela}>
      <Stack.Screen options={{ title: paciente.nome }} />
      <AvisoServidor />
      <ScrollView
        contentContainerStyle={base.conteudo}
        refreshControl={<RefreshControl refreshing={false} onRefresh={recarregar} colors={[cores.marca]} />}
      >
        <View style={estilos.cabecalho}>
          <View style={{ flex: 1 }}>
            <Text style={base.suave}>
              {paciente.idade} anos · {paciente.leito}
            </Text>
            <Text style={base.suave}>
              {erro ? `Falha na atualização: ${erro}` : atualizadoEm ? `Atualizado às ${formatarHora(atualizadoEm)}` : ''}
            </Text>
          </View>
          {ultima && <SeloEstado estado={ultima.estado} />}
        </View>

        <View style={base.cartao}>
          <View style={estilos.tituloLinha}>
            <Text style={base.tituloCartao}>Risco de pico previsto</Text>
            {ehMedico && (
              <Pressable style={base.botaoSecundario} onPress={reavaliar} disabled={reavaliando}>
                <Text style={base.botaoSecundarioTexto}>{reavaliando ? 'Reavaliando…' : 'Reavaliar'}</Text>
              </Pressable>
            )}
          </View>
          {erroAvaliacao && <Text style={base.erro}>{erroAvaliacao}</Text>}
          {avaliacao ? <ResumoRisco avaliacao={avaliacao} /> : <Text style={base.suave}>Ainda sem avaliação de risco.</Text>}
        </View>

        <View style={base.cartao}>
          <View style={estilos.tituloLinha}>
            <Text style={base.tituloCartao}>Sinais vitais</Text>
            {ultima && <Text style={base.suave}>{tempoRelativo(ultima.ts)}</Text>}
          </View>
          {leituras.length === 0 ? (
            <Text style={base.suave}>Aguardando a primeira leitura do dispositivo.</Text>
          ) : (
            <SinaisVitais leituras={leituras} />
          )}
        </View>

        <Pressable
          style={({ pressed }) => [base.botao, pressed && { opacity: 0.8 }]}
          onPress={() => router.push(`/chat/${paciente.id}`)}
          accessibilityRole="button"
        >
          <Text style={base.botaoTexto}>Conversar com o assistente</Text>
        </Pressable>

        {avaliacao && <Recomendacao avaliacao={avaliacao} />}

        <Text style={estilos.aviso}>{avaliacao?.aviso_legal ?? AVISO_PADRAO}</Text>
      </ScrollView>
    </View>
  )
}

function ResumoRisco({ avaliacao }: { avaliacao: RespostaAtendimento }) {
  const r = avaliacao.avaliacao_risco
  return (
    <>
      <MedidorRisco probabilidade={r.probabilidade} classificacao={r.classificacao} />
      <View style={estilos.grade}>
        <Detalhe rotulo="Classificação">
          <SeloRisco classificacao={r.classificacao} />
        </Detalhe>
        <Detalhe rotulo="Pico previsto">
          <Text style={estilos.detalheValor}>{r.pico_risco_previsto ? 'Sim' : 'Não'}</Text>
        </Detalhe>
        <Detalhe rotulo="Protocolos acionados">
          <Text style={estilos.detalheValor}>{avaliacao.protocolos.length}</Text>
        </Detalhe>
        <Detalhe rotulo="Avaliado">
          <Text style={estilos.detalheValor}>{tempoRelativo(avaliacao.gerado_em)}</Text>
        </Detalhe>
      </View>
    </>
  )
}

function Detalhe({ rotulo, children }: { rotulo: string; children: React.ReactNode }) {
  return (
    <View style={estilos.detalhe}>
      <Text style={base.suave}>{rotulo}</Text>
      {children}
    </View>
  )
}

const SERIES = [
  { chave: 'fc', rotulo: 'Frequência cardíaca', unidade: 'bpm', limiar: 110, min: 40, max: 160, alerta: (v: number) => v > 110 },
  { chave: 'spo2', rotulo: 'SpO₂', unidade: '%', limiar: 92, min: 80, max: 100, alerta: (v: number) => v < 92 },
  { chave: 'temperatura', rotulo: 'Temperatura', unidade: '°C', limiar: 38, min: 35, max: 40, alerta: (v: number) => v > 38 },
] as const

function SinaisVitais({ leituras }: { leituras: Leitura[] }) {
  const [largura, setLargura] = useState(0)
  const ultima = leituras[leituras.length - 1]
  return (
    <View style={{ gap: 12 }} onLayout={(e) => setLargura(e.nativeEvent.layout.width)}>
      {SERIES.map((s) => {
        const valor = ultima[s.chave]
        const alerta = s.alerta(valor)
        return (
          <View key={s.chave} style={[estilos.sinal, alerta && { backgroundColor: cores.altoFundo }]}>
            <View style={estilos.tituloLinha}>
              <Text style={base.suave}>{s.rotulo}</Text>
              {alerta && <Text style={estilos.alerta}>acima do limiar de risco</Text>}
            </View>
            <Text style={estilos.sinalValor}>
              {formatarNumero(valor)}
              <Text style={base.suave}> {s.unidade}</Text>
            </Text>
            <Tendencia
              valores={leituras.map((l) => l[s.chave])}
              limiar={s.limiar}
              min={s.min}
              max={s.max}
              largura={Math.max(largura - 24, 0)}
            />
          </View>
        )
      })}
    </View>
  )
}

function Recomendacao({ avaliacao }: { avaliacao: RespostaAtendimento }) {
  return (
    <View style={base.cartao}>
      <Text style={base.tituloCartao}>Recomendação</Text>
      <Text style={base.suave}>
        Origem: {ROTULO_ORIGEM[avaliacao.origem]}
        {avaliacao.motivo_fallback ? ` (${avaliacao.motivo_fallback})` : ''}
      </Text>
      <Text style={[base.texto, estilos.explicacao]}>{avaliacao.explicacao}</Text>

      <Text style={estilos.subtitulo}>Protocolos acionados</Text>
      {avaliacao.protocolos.length === 0 ? (
        <Text style={base.suave}>Nenhum protocolo acionado.</Text>
      ) : (
        avaliacao.protocolos.map((p) => (
          <View key={p.id} style={estilos.protocolo}>
            <Text style={estilos.protocoloId}>{p.id}</Text>
            <View style={{ flex: 1 }}>
              <Text style={base.texto}>{p.texto}</Text>
              <Text style={estilos.mono}>{p.justificativa}</Text>
            </View>
          </View>
        ))
      )}

      {avaliacao.sinais_de_atencao.length > 0 && (
        <>
          <Text style={estilos.subtitulo}>Sinais de atenção</Text>
          {avaliacao.sinais_de_atencao.map((s) => (
            <Text key={s.variavel} style={base.texto}>
              • <Text style={{ fontWeight: '700' }}>{ROTULO_VARIAVEL[s.variavel] ?? s.variavel}</Text> em{' '}
              {formatarNumero(s.valor)}: o {s.protocolo_id} aciona em {formatarNumero(s.limiar_protocolo)}.
            </Text>
          ))}
        </>
      )}

      <Text style={estilos.subtitulo}>Ações operacionais</Text>
      {avaliacao.acoes_operacionais.map((a, i) => (
        <Text key={a} style={base.texto}>
          {i + 1}. {a}
        </Text>
      ))}
    </View>
  )
}

const estilos = StyleSheet.create({
  centro: { alignItems: 'center', justifyContent: 'center', padding: 16 },
  cabecalho: { flexDirection: 'row', alignItems: 'center', gap: 12 },
  tituloLinha: { flexDirection: 'row', alignItems: 'center', justifyContent: 'space-between', gap: 8 },
  grade: { flexDirection: 'row', flexWrap: 'wrap', rowGap: 12 },
  detalhe: { width: '50%', gap: 2 },
  detalheValor: { fontSize: 15, fontWeight: '700', color: cores.texto },
  sinal: { backgroundColor: cores.superficie2, borderRadius: 10, padding: 12, gap: 4 },
  sinalValor: { fontSize: 26, fontWeight: '800', color: cores.texto },
  alerta: { fontSize: 11, fontWeight: '700', color: cores.alto },
  explicacao: { backgroundColor: cores.superficie2, borderRadius: 10, padding: 12 },
  subtitulo: { fontSize: 15, fontWeight: '700', color: cores.texto, marginTop: 4 },
  protocolo: { flexDirection: 'row', gap: 10 },
  protocoloId: {
    alignSelf: 'flex-start',
    backgroundColor: cores.altoFundo,
    color: cores.alto,
    fontWeight: '800',
    fontSize: 12,
    paddingHorizontal: 8,
    paddingVertical: 2,
    borderRadius: 6,
    overflow: 'hidden',
  },
  mono: { fontFamily: 'monospace', fontSize: 12, color: cores.textoSuave },
  aviso: {
    fontSize: 12,
    color: cores.textoSuave,
    borderLeftWidth: 3,
    borderLeftColor: cores.moderado,
    backgroundColor: cores.superficie,
    padding: 12,
  },
})
