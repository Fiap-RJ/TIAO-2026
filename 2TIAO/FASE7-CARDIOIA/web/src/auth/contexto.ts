import { createContext } from 'react'
import type { Usuario } from '../api/types'

export interface AuthValor {
  usuario: Usuario | null
  entrar: (email: string, senha: string) => Promise<Usuario>
  sair: () => void
}

export const AuthContext = createContext<AuthValor | null>(null)
