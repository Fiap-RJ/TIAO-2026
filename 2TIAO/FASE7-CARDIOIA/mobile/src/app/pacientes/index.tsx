import { Redirect, router } from 'expo-router'
import { FlatList, Pressable, RefreshControl, StyleSheet, Text, View } from 'react-native'
import { api } from '../../api/client'
import type { Classificacao, PacienteResumo } from '../../api/types'
import { rotaInicial, useSessao } from '../../auth/sessao'
import { AvisoServidor } from '../../components/AvisoServidor'
import { SeloEstado, SeloRisco } from '../../components/Indicadores'
import { usePolling } from '../../hooks/usePolling'
import { formatarNumero, formatarPercentual, tempoRelativo } from '../../lib/format'
import { base, cores, corFaixa } from '../../theme'

const ORDEM: Record<Classificacao, number> = { ALTO: 0, MODERADO: 1, BAIXO: 2 }

function ordenar(lista: PacienteResumo[]): PacienteResumo[] {
  return [...lista].sort(
    (a, b) =>
      (a.classificacao ? ORDEM[a.classificacao] : 3) - (b.classificacao ? ORDEM[b.classificacao] : 3) ||
      (b.probabilidade ?? 0) - (a.probabilidade ?? 0),
  )
}

export default function Pacientes() {
  const { usuario } = useSessao()
  const { dados, erro, carregando, recarregar } = usePolling(api.listarPacientes, 10_000)

  if (usuario && usuario.perfil !== 'medico') return <Redirect href={rotaInicial(usuario)} />

  return (
    <View style={base.tela}>
      <AvisoServidor />
      <FlatList
        data={ordenar(dados ?? [])}
        keyExtractor={(p) => p.id}
        contentContainerStyle={base.conteudo}
        refreshControl={<RefreshControl refreshing={false} onRefresh={recarregar} colors={[cores.marca]} />}
        ListHeaderComponent={
          <View style={{ gap: 8 }}>
            <Text style={base.suave}>Ordenados pelo risco de pico previsto. Atualiza a cada 10 s.</Text>
            {erro && <Text style={base.erro}>{erro}</Text>}
          </View>
        }
        ListEmptyComponent={
          <Text style={base.suave}>{carregando ? 'Carregando pacientes…' : 'Nenhum paciente cadastrado.'}</Text>
        }
        renderItem={({ item: p }) => (
            <Pressable
              onPress={() => router.push(`/pacientes/${p.id}`)}
              style={({ pressed }) => [
                base.cartao,
                estilos.item,
                { borderLeftColor: p.classificacao ? corFaixa[p.classificacao].cor : cores.borda },
                pressed && { opacity: 0.85 },
              ]}
              accessibilityRole="button"
              accessibilityLabel={`${p.nome}, ${p.classificacao ?? 'sem avaliação'}`}
            >
              <View>
                <Text style={estilos.nome}>{p.nome}</Text>
                <Text style={base.suave}>
                  {p.idade} anos · {p.leito}
                </Text>
              </View>
              {p.ultima_leitura && (
                <View style={estilos.sinais}>
                  <Text style={base.suave}>
                    <Text style={estilos.valor}>{p.ultima_leitura.fc}</Text> bpm
                  </Text>
                  <Text style={base.suave}>
                    <Text style={estilos.valor}>{p.ultima_leitura.spo2}</Text>% SpO₂
                  </Text>
                  <Text style={base.suave}>
                    <Text style={estilos.valor}>{formatarNumero(p.ultima_leitura.temperatura)}</Text> °C
                  </Text>
                </View>
              )}
              <View style={estilos.linha}>
                <SeloRisco classificacao={p.classificacao} />
                {p.probabilidade !== null && <Text style={estilos.prob}>{formatarPercentual(p.probabilidade)}</Text>}
              </View>
              {p.ultima_leitura && (
                <View style={[estilos.linha, { justifyContent: 'space-between' }]}>
                  <SeloEstado estado={p.ultima_leitura.estado} />
                  <Text style={base.suave}>{tempoRelativo(p.ultima_leitura.ts)}</Text>
                </View>
              )}
            </Pressable>
        )}
      />
    </View>
  )
}

const estilos = StyleSheet.create({
  item: { borderLeftWidth: 5 },
  nome: { fontSize: 17, fontWeight: '700', color: cores.texto },
  sinais: { flexDirection: 'row', gap: 16, flexWrap: 'wrap' },
  valor: { fontSize: 18, fontWeight: '700', color: cores.texto },
  linha: { flexDirection: 'row', alignItems: 'center', gap: 10 },
  prob: { fontSize: 22, fontWeight: '800', color: cores.texto },
})
