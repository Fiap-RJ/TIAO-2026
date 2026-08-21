import { useState } from 'react';
import logoGenera from '../../assets/logo-genera.png';
import { usePacienteId } from '../../hooks/usePacienteId';
import MessageBubble from './MessageBubble';

/**
 * ChatWindow — interface de chat com o agente (A5).
 * Extraído do App.jsx original, mantendo o comportamento 1:1: envio de
 * mensagem, upload de PDF (mock) e exibição de fontes. Usa usePacienteId em
 * vez do id hardcoded e MessageBubble para renderizar as mensagens.
 */
export default function ChatWindow() {
  const pacienteId = usePacienteId();
  const [mensagens, setMensagens] = useState([]);
  const [inputUsuario, setInputUsuario] = useState('');
  const [carregando, setCarregando] = useState(false);

  const enviarMensagem = async () => {
    if (!inputUsuario) return;

    const novaMensagemPaciente = { remetente: 'paciente', texto: inputUsuario };
    setMensagens((msgsAntigas) => [...msgsAntigas, novaMensagemPaciente]);
    setInputUsuario('');
    setCarregando(true);

    try {
      const resposta = await fetch('/api/chat/', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          Accept: 'application/json',
        },
        body: JSON.stringify({
          paciente_id: pacienteId,
          mensagem: novaMensagemPaciente.texto,
        }),
      });

      if (!resposta.ok) {
        throw new Error('Falha na comunicação com a API do servidor');
      }

      const dadosIA = await resposta.json();

      const novaMensagemIA = {
        remetente: 'ia',
        texto:
          dadosIA.resposta ||
          dadosIA.texto ||
          'Resposta recebida, mas formato inesperado.',
        fontes: dadosIA.fontes || [],
      };

      setMensagens((msgsAntigas) => [...msgsAntigas, novaMensagemIA]);
    } catch (erro) {
      console.error('Erro detalhado na requisição:', erro);
      const mensagemErro = {
        remetente: 'ia',
        texto:
          'Ocorreu um erro de conexão com o motor vetorial. Verifique se o servidor local está operacional e se as políticas de CORS permitem a comunicação.',
        fontes: [],
      };
      setMensagens((msgsAntigas) => [...msgsAntigas, mensagemErro]);
    } finally {
      setCarregando(false);
    }
  };

  const lidarComUpload = (evento) => {
    const arquivo = evento.target.files[0];
    if (arquivo) {
      const msgUpload = {
        remetente: 'ia',
        texto: `O arquivo PDF "${arquivo.name}" foi processado. O que gostaria de saber sobre as suas predisposições?`,
      };
      setMensagens((msgsAntigas) => [...msgsAntigas, msgUpload]);
    }
  };

  return (
    <div className="mx-auto flex h-[75vh] w-full max-w-4xl flex-col overflow-hidden rounded-xl border border-gray-300 bg-white shadow-lg">
      {/* Cabeçalho */}
      <div className="relative z-10 flex flex-col items-center border-b border-gray-300 bg-white p-6 text-center shadow-md">
        <img src={logoGenera} alt="Genera" className="mb-3 h-16 object-contain" />
        <p className="text-sm font-medium uppercase tracking-widest text-genera-roxo/70">
          Assistente Especializado
        </p>
      </div>

      {/* Área de Mensagens */}
      <div className="flex-1 space-y-6 overflow-y-auto bg-gray-50 p-6 shadow-inner">
        {mensagens.length === 0 ? (
          <div className="mt-20 text-center text-lg font-light text-genera-roxo/50">
            Faça o upload do seu laudo em PDF ou digite a sua dúvida clínica
            abaixo.
          </div>
        ) : (
          mensagens.map((msg, index) => (
            <MessageBubble
              key={index}
              remetente={msg.remetente}
              texto={msg.texto}
              fontes={msg.fontes}
            />
          ))
        )}
        {carregando && (
          <div className="text-left">
            <p className="inline-block rounded-2xl rounded-bl-none border border-gray-200 bg-white p-4 text-sm italic text-genera-roxo shadow-sm">
              A processar os dados genéticos...
            </p>
          </div>
        )}
      </div>

      {/* Área de Input */}
      <div className="relative z-10 flex flex-col gap-4 border-t border-gray-200 bg-white p-5 shadow-[0_-4px_6px_-1px_rgba(0,0,0,0.05)]">
        <div className="flex justify-start">
          <label className="flex cursor-pointer items-center gap-2 rounded-full border-2 border-genera-magenta px-6 py-2 font-medium text-genera-magenta shadow-sm transition-all duration-300 hover:bg-genera-magenta hover:text-white">
            <svg
              xmlns="http://www.w3.org/2000/svg"
              fill="none"
              viewBox="0 0 24 24"
              strokeWidth={2}
              stroke="currentColor"
              className="h-5 w-5"
              aria-hidden="true"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                d="M18.375 12.739l-7.693 7.693a4.536 4.536 0 01-6.42-6.421l10.899-10.899m-7.828 7.828l-5.656 5.656a2.268 2.268 0 003.207 3.207l5.657-5.657m5.656-5.656l-3.182 3.182"
              />
            </svg>
            Anexar Laudo PDF
            <input
              type="file"
              accept=".pdf"
              className="hidden"
              onChange={lidarComUpload}
            />
          </label>
        </div>

        <div className="flex w-full items-center gap-3">
          <input
            type="text"
            className="flex-1 rounded-full border-2 border-gray-200 bg-gray-50 p-4 text-genera-roxo placeholder-gray-400 shadow-inner transition-colors focus:border-genera-magenta focus:outline-none"
            placeholder="Digite sua dúvida clínica..."
            value={inputUsuario}
            onChange={(e) => setInputUsuario(e.target.value)}
            onKeyDown={(e) => e.key === 'Enter' && enviarMensagem()}
          />
          <button
            className="flex items-center gap-2 rounded-full bg-genera-magenta px-8 py-4 font-bold text-white shadow-md transition-colors hover:bg-genera-magentahover"
            onClick={enviarMensagem}
          >
            Enviar
            <svg
              xmlns="http://www.w3.org/2000/svg"
              fill="none"
              viewBox="0 0 24 24"
              strokeWidth={2}
              stroke="currentColor"
              className="h-5 w-5"
              aria-hidden="true"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                d="M6 12L3.269 3.126A59.768 59.768 0 0121.485 12 59.77 59.77 0 013.27 20.876L5.999 12zm0 0h7.5"
              />
            </svg>
          </button>
        </div>
      </div>
    </div>
  );
}
