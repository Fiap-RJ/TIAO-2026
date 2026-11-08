import { useEffect, useRef, useState, type FormEvent } from 'react'
import { api, ApiError } from '../api/client'

interface Mensagem {
  autor: 'usuario' | 'assistente' | 'erro'
  texto: string
}

const SUGESTOES = ['Por que o risco está assim?', 'O que significa cada protocolo?', 'Estou com dor no peito']

export function Chat({ pacienteId }: { pacienteId: string | null }) {
  const [mensagens, setMensagens] = useState<Mensagem[]>([
    {
      autor: 'assistente',
      texto: 'Olá! Sou o assistente da CardioIA. Posso explicar os indicadores e a classificação de risco.',
    },
  ])
  const [texto, setTexto] = useState('')
  const [enviando, setEnviando] = useState(false)
  const sessaoId = useRef<string | null>(null)
  const fim = useRef<HTMLDivElement>(null)

  useEffect(() => {
    fim.current?.scrollIntoView({ block: 'nearest' })
  }, [mensagens])

  async function enviar(conteudo: string) {
    const limpo = conteudo.trim()
    if (!limpo || enviando) return
    setMensagens((atual) => [...atual, { autor: 'usuario', texto: limpo }])
    setTexto('')
    setEnviando(true)
    try {
      const resposta = await api.enviarMensagem({
        mensagem: limpo,
        paciente_id: pacienteId,
        sessao_id: sessaoId.current,
      })
      sessaoId.current = resposta.sessao_id
      setMensagens((atual) => [...atual, { autor: 'assistente', texto: resposta.resposta }])
    } catch (e) {
      const erro = e instanceof ApiError ? e.message : 'Não foi possível enviar a mensagem.'
      setMensagens((atual) => [...atual, { autor: 'erro', texto: erro }])
    } finally {
      setEnviando(false)
    }
  }

  function aoEnviar(evento: FormEvent) {
    evento.preventDefault()
    void enviar(texto)
  }

  return (
    <section className="cartao chat" aria-label="Assistente CardioIA">
      <h3>Assistente CardioIA</h3>
      <div className="chat-mensagens" aria-live="polite">
        {mensagens.map((m, i) => (
          <p key={i} className={`balao balao-${m.autor}`}>
            {m.texto}
          </p>
        ))}
        {enviando && <p className="balao balao-assistente digitando">digitando…</p>}
        <div ref={fim} />
      </div>
      <div className="sugestoes">
        {SUGESTOES.map((s) => (
          <button key={s} type="button" className="chip chip-botao" onClick={() => void enviar(s)} disabled={enviando}>
            {s}
          </button>
        ))}
      </div>
      <form className="chat-form" onSubmit={aoEnviar}>
        <label htmlFor="chat-texto" className="sr-only">
          Mensagem
        </label>
        <input
          id="chat-texto"
          value={texto}
          onChange={(e) => setTexto(e.target.value)}
          placeholder="Escreva sua pergunta…"
          autoComplete="off"
          maxLength={500}
        />
        <button type="submit" className="botao" disabled={enviando || !texto.trim()}>
          Enviar
        </button>
      </form>
    </section>
  )
}
