import { router } from 'expo-router'
import { useState } from 'react'
import {
  ActivityIndicator,
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
import Svg, { Path } from 'react-native-svg'
import { ApiError, USANDO_MOCK } from '../api/client'
import { CREDENCIAIS_DEMO } from '../api/mock'
import { rotaInicial, useSessao } from '../auth/sessao'
import { AvisoServidor } from '../components/AvisoServidor'
import { base, cores } from '../theme'

function Logo() {
  return (
    <Svg width={48} height={48} viewBox="0 0 32 32">
      <Path d="M16 28s-11-6.6-11-15A6 6 0 0 1 16 9.5 6 6 0 0 1 27 13c0 8.4-11 15-11 15z" fill={cores.marca} />
      <Path d="M7 16h5l2-4 3 8 2-4h6" fill="none" stroke="#fff" strokeWidth={2} strokeLinecap="round" strokeLinejoin="round" />
    </Svg>
  )
}

export default function Login() {
  const { entrar } = useSessao()
  const [email, setEmail] = useState('')
  const [senha, setSenha] = useState('')
  const [erro, setErro] = useState<string | null>(null)
  const [enviando, setEnviando] = useState(false)

  async function aoEntrar() {
    setErro(null)
    setEnviando(true)
    try {
      const usuario = await entrar(email, senha)
      router.replace(rotaInicial(usuario))
    } catch (e) {
      setErro(e instanceof ApiError ? e.message : 'Não foi possível entrar.')
      setEnviando(false)
    }
  }

  return (
    <SafeAreaView style={base.tela}>
      <AvisoServidor />
      <KeyboardAvoidingView style={{ flex: 1 }} behavior={Platform.OS === 'ios' ? 'padding' : undefined}>
        <ScrollView contentContainerStyle={estilos.conteudo} keyboardShouldPersistTaps="handled">
          <View style={estilos.marca}>
            <Logo />
            <View>
              <Text style={estilos.titulo}>CardioIA</Text>
              <Text style={base.suave}>Plataforma de inteligência cardíaca</Text>
            </View>
          </View>

          <View style={base.cartao}>
            <Text style={estilos.rotulo}>E-mail</Text>
            <TextInput
              style={base.input}
              value={email}
              onChangeText={setEmail}
              autoCapitalize="none"
              autoComplete="email"
              keyboardType="email-address"
              textContentType="username"
              accessibilityLabel="E-mail"
            />
            <Text style={estilos.rotulo}>Senha</Text>
            <TextInput
              style={base.input}
              value={senha}
              onChangeText={setSenha}
              secureTextEntry
              autoComplete="password"
              textContentType="password"
              onSubmitEditing={aoEntrar}
              accessibilityLabel="Senha"
            />
            {erro && <Text style={base.erro}>{erro}</Text>}
            <Pressable
              style={({ pressed }) => [base.botao, (enviando || !email || !senha) && { opacity: 0.55 }, pressed && { opacity: 0.8 }]}
              onPress={aoEntrar}
              disabled={enviando || !email || !senha}
              accessibilityRole="button"
            >
              {enviando ? <ActivityIndicator color="#fff" /> : <Text style={base.botaoTexto}>Entrar</Text>}
            </Pressable>
          </View>

          {USANDO_MOCK && (
            <View style={estilos.demo}>
              <Text style={base.suave}>Modo demonstração: toque para preencher</Text>
              {CREDENCIAIS_DEMO.map((c) => (
                <Pressable
                  key={c.email}
                  style={base.botaoSecundario}
                  onPress={() => {
                    setEmail(c.email)
                    setSenha(c.senha)
                  }}
                >
                  <Text style={base.botaoSecundarioTexto}>
                    {c.perfil}: {c.email}
                  </Text>
                </Pressable>
              ))}
            </View>
          )}
        </ScrollView>
      </KeyboardAvoidingView>
    </SafeAreaView>
  )
}

const estilos = StyleSheet.create({
  conteudo: { flexGrow: 1, justifyContent: 'center', padding: 20, gap: 20 },
  marca: { flexDirection: 'row', alignItems: 'center', gap: 12 },
  titulo: { fontSize: 28, fontWeight: '800', color: cores.texto },
  rotulo: { fontWeight: '600', color: cores.texto, marginBottom: -4 },
  demo: { gap: 8 },
})
