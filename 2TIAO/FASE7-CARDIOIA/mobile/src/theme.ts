import { StyleSheet } from 'react-native'
import type { Classificacao, EstadoDispositivo } from './api/types'

export const cores = {
  marca: '#c8102e',
  fundo: '#f5f6f8',
  superficie: '#ffffff',
  superficie2: '#f0f2f5',
  borda: '#dfe3e8',
  texto: '#1b1f24',
  textoSuave: '#5b6470',
  baixo: '#1f8a4c',
  baixoFundo: '#e5f4ea',
  moderado: '#b26a00',
  moderadoFundo: '#fdf1dc',
  alto: '#c8102e',
  altoFundo: '#fbe5e8',
}

export const corFaixa: Record<Classificacao, { cor: string; fundo: string }> = {
  BAIXO: { cor: cores.baixo, fundo: cores.baixoFundo },
  MODERADO: { cor: cores.moderado, fundo: cores.moderadoFundo },
  ALTO: { cor: cores.alto, fundo: cores.altoFundo },
}

export const corEstado: Record<EstadoDispositivo, { cor: string; fundo: string }> = {
  normal: corFaixa.BAIXO,
  atencao: corFaixa.MODERADO,
  critico: corFaixa.ALTO,
}

export const base = StyleSheet.create({
  tela: { flex: 1, backgroundColor: cores.fundo },
  conteudo: { padding: 16, gap: 16 },
  cartao: {
    backgroundColor: cores.superficie,
    borderRadius: 12,
    borderWidth: 1,
    borderColor: cores.borda,
    padding: 16,
    gap: 12,
  },
  tituloCartao: { fontSize: 16, fontWeight: '700', color: cores.texto },
  texto: { fontSize: 15, color: cores.texto },
  suave: { fontSize: 13, color: cores.textoSuave },
  erro: {
    backgroundColor: cores.altoFundo,
    color: cores.alto,
    padding: 12,
    borderRadius: 8,
    fontWeight: '500',
  },
  botao: {
    backgroundColor: cores.marca,
    borderRadius: 10,
    paddingVertical: 14,
    paddingHorizontal: 18,
    alignItems: 'center',
  },
  botaoTexto: { color: '#fff', fontWeight: '700', fontSize: 16 },
  botaoSecundario: {
    borderWidth: 1,
    borderColor: cores.borda,
    borderRadius: 10,
    paddingVertical: 10,
    paddingHorizontal: 14,
    alignItems: 'center',
  },
  botaoSecundarioTexto: { color: cores.texto, fontWeight: '600' },
  input: {
    borderWidth: 1,
    borderColor: cores.borda,
    borderRadius: 10,
    paddingHorizontal: 14,
    paddingVertical: 12,
    fontSize: 16,
    backgroundColor: cores.superficie,
    color: cores.texto,
  },
})
