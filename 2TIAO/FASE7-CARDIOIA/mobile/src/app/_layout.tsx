import { Stack } from 'expo-router'
import { StatusBar } from 'expo-status-bar'
import { ActivityIndicator, Pressable, Text, View } from 'react-native'
import { SafeAreaProvider } from 'react-native-safe-area-context'
import { SessaoProvider, useSessao } from '../auth/sessao'
import { cores } from '../theme'

function BotaoSair() {
  const { sair } = useSessao()
  return (
    <Pressable onPress={sair} hitSlop={12} accessibilityRole="button" style={{ paddingHorizontal: 8 }}>
      <Text style={{ color: cores.marca, fontWeight: '700', fontSize: 15 }}>Sair</Text>
    </Pressable>
  )
}

function Navegacao() {
  const { usuario, carregando } = useSessao()

  if (carregando) {
    return (
      <View style={{ flex: 1, alignItems: 'center', justifyContent: 'center', backgroundColor: cores.fundo }}>
        <ActivityIndicator color={cores.marca} size="large" />
      </View>
    )
  }

  const logado = usuario !== null

  return (
    <Stack
      screenOptions={{
        headerTintColor: cores.texto,
        headerStyle: { backgroundColor: cores.superficie },
        headerTitleStyle: { fontWeight: '700' },
        contentStyle: { backgroundColor: cores.fundo },
        headerRight: logado ? () => <BotaoSair /> : undefined,
      }}
    >
      <Stack.Screen name="index" options={{ headerShown: false }} />
      <Stack.Protected guard={!logado}>
        <Stack.Screen name="login" options={{ headerShown: false }} />
      </Stack.Protected>
      <Stack.Protected guard={logado} redirectTo="/login">
        <Stack.Screen name="pacientes/index" options={{ title: 'Pacientes' }} />
        <Stack.Screen name="pacientes/[id]" options={{ title: 'Painel do paciente' }} />
        <Stack.Screen name="chat/[id]" options={{ title: 'Assistente CardioIA' }} />
      </Stack.Protected>
    </Stack>
  )
}

export default function RootLayout() {
  return (
    <SafeAreaProvider>
      <SessaoProvider>
        <StatusBar style="dark" />
        <Navegacao />
      </SessaoProvider>
    </SafeAreaProvider>
  )
}
