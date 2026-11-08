import { useEffect, useState } from 'react'
import { StyleSheet, Text, View } from 'react-native'
import { observarLentidao, USANDO_MOCK } from '../api/client'
import { cores } from '../theme'

/** Faixa no topo: modo demonstração e servidor acordando (cold start do Render). */
export function AvisoServidor() {
  const [lento, setLento] = useState(false)
  useEffect(() => observarLentidao(setLento), [])

  if (!lento && !USANDO_MOCK) return null
  return (
    <View style={[estilos.faixa, lento ? estilos.lento : estilos.mock]} accessibilityRole="alert">
      <Text style={[estilos.texto, { color: lento ? cores.moderado : cores.textoSuave }]}>
        {lento
          ? 'O servidor está iniciando (pode levar até um minuto)…'
          : 'Modo demonstração: dados simulados no aparelho'}
      </Text>
    </View>
  )
}

const estilos = StyleSheet.create({
  faixa: { paddingVertical: 6, paddingHorizontal: 16 },
  lento: { backgroundColor: cores.moderadoFundo },
  mock: { backgroundColor: cores.superficie2 },
  texto: { fontSize: 12, fontWeight: '600', textAlign: 'center' },
})
