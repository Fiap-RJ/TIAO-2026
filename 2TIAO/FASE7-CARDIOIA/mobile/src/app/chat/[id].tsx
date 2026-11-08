import { useLocalSearchParams } from 'expo-router'
import { useRef, useState } from 'react'
import {
  FlatList,
  KeyboardAvoidingView,
  Platform,
  Pressable,
  ScrollView,
  StyleSheet,
  Text,
  TextInput,
  View,
} from 'react-native'
import { SafeAreaView } from 'react-native-safe-area-context'
import { api, ApiError } from '../../api/client'
import { AvisoServidor } from '../../components/AvisoServidor'
import { base, cores } from '../../theme'

interface Mensagem {
  id: number
  autor: 'usuario' | 'assistente' | 'erro'
  texto: string
}

const SUGESTOES = ['Por que o risco está assim?', 'O que significa cada protocolo?', 'Estou com dor no peito']

export default function Chat() {
  const { id } = useLocalSearchParams<{ id: string }>()
  const [mensagens, setMensagens] = useState<Mensagem[]>([
    {
      id: 0,
      autor: 'assistente',
      texto: 'Olá! Sou o assistente da CardioIA. Posso explicar os indicadores e a classificação de risco.',
    },
  ])
  const [texto, setTexto] = useState('')
  const [enviando, setEnviando] = useState(false)
  const sessaoId = useRef<string | null>(null)
  const proximoId = useRef(1)
  const lista = useRef<FlatList<Mensagem>>(null)

  function adicionar(autor: Mensagem['autor'], conteudo: string) {
    const nova = { id: proximoId.current++, autor, texto: conteudo }
    setMensagens((atual) => [...atual, nova])
  }

  async function enviar(conteudo: string) {
    const limpo = conteudo.trim()
    if (!limpo || enviando) return
    adicionar('usuario', limpo)
    setTexto('')
    setEnviando(true)
    try {
      const resposta = await api.enviarMensagem({ mensagem: limpo, paciente_id: id, sessao_id: sessaoId.current })
      sessaoId.current = resposta.sessao_id
      adicionar('assistente', resposta.resposta)
    } catch (e) {
      adicionar('erro', e instanceof ApiError ? e.message : 'Não foi possível enviar a mensagem.')
    } finally {
      setEnviando(false)
    }
  }

  return (
    <SafeAreaView style={base.tela} edges={['bottom']}>
      <AvisoServidor />
      <KeyboardAvoidingView
        style={{ flex: 1 }}
        behavior={Platform.OS === 'ios' ? 'padding' : 'height'}
        keyboardVerticalOffset={Platform.OS === 'ios' ? 90 : 0}
      >
        <FlatList
          ref={lista}
          data={mensagens}
          keyExtractor={(m) => String(m.id)}
          contentContainerStyle={estilos.mensagens}
          onContentSizeChange={() => lista.current?.scrollToEnd({ animated: true })}
          renderItem={({ item }) => (
            <Text style={[estilos.balao, estilos[item.autor]]}>{item.texto}</Text>
          )}
          ListFooterComponent={
            enviando ? <Text style={[estilos.balao, estilos.assistente, estilos.digitando]}>digitando…</Text> : undefined
          }
        />
        <ScrollView
          horizontal
          style={{ flexGrow: 0 }}
          showsHorizontalScrollIndicator={false}
          contentContainerStyle={estilos.sugestoes}
        >
          {SUGESTOES.map((s) => (
            <Pressable key={s} style={estilos.sugestao} onPress={() => enviar(s)} disabled={enviando}>
              <Text style={{ color: cores.texto }}>{s}</Text>
            </Pressable>
          ))}
        </ScrollView>
        <View style={estilos.form}>
          <TextInput
            style={[base.input, { flex: 1 }]}
            value={texto}
            onChangeText={setTexto}
            placeholder="Escreva sua pergunta…"
            placeholderTextColor={cores.textoSuave}
            maxLength={500}
            onSubmitEditing={() => enviar(texto)}
            returnKeyType="send"
            accessibilityLabel="Mensagem"
          />
          <Pressable
            style={[base.botao, (enviando || !texto.trim()) && { opacity: 0.55 }]}
            onPress={() => enviar(texto)}
            disabled={enviando || !texto.trim()}
            accessibilityRole="button"
          >
            <Text style={base.botaoTexto}>Enviar</Text>
          </Pressable>
        </View>
      </KeyboardAvoidingView>
    </SafeAreaView>
  )
}

const estilos = StyleSheet.create({
  mensagens: { padding: 16, gap: 8 },
  balao: { maxWidth: '85%', paddingHorizontal: 12, paddingVertical: 8, borderRadius: 12, fontSize: 15, overflow: 'hidden' },
  usuario: { alignSelf: 'flex-end', backgroundColor: cores.marca, color: '#fff' },
  assistente: { alignSelf: 'flex-start', backgroundColor: cores.superficie, color: cores.texto },
  erro: { alignSelf: 'flex-start', backgroundColor: cores.altoFundo, color: cores.alto },
  digitando: { color: cores.textoSuave, fontStyle: 'italic', marginTop: 8 },
  sugestoes: { gap: 8, paddingHorizontal: 16, paddingVertical: 8 },
  sugestao: {
    alignSelf: 'center',
    borderWidth: 1,
    borderColor: cores.borda,
    borderRadius: 999,
    paddingHorizontal: 12,
    paddingVertical: 6,
    backgroundColor: cores.superficie,
  },
  form: {
    flexDirection: 'row',
    gap: 8,
    padding: 12,
    borderTopWidth: 1,
    borderTopColor: cores.borda,
    backgroundColor: cores.superficie,
  },
})
