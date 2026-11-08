import { Redirect } from 'expo-router'
import { rotaInicial, useSessao } from '../auth/sessao'

export default function Inicio() {
  const { usuario } = useSessao()
  return <Redirect href={usuario ? rotaInicial(usuario) : '/login'} />
}
