import { useState } from 'react';
import logoGenera from './assets/logo-genera.png'

export default function App() {
  const [mensagens, setMensagens] = useState([]);
  const [inputUsuario, setInputUsuario] = useState('');
  const [carregando, setCarregando] = useState(false);

  const enviarMensagem = async () => {
    if (!inputUsuario) return;
    
    const novaMensagemPaciente = { remetente: 'paciente', texto: inputUsuario };
    setMensagens(msgsAntigas => [...msgsAntigas, novaMensagemPaciente]);
    setInputUsuario('');
    setCarregando(true);

    try {
      const resposta = await fetch('/api/chat/', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Accept': 'application/json'
        },
        body: JSON.stringify({
          paciente_id: "uuid-123",
          mensagem: novaMensagemPaciente.texto
        })
      });

      if (!resposta.ok) {
        throw new Error('Falha na comunicação com a API do servidor');
      }

      const dadosIA = await resposta.json();
      
      const novaMensagemIA = { 
        remetente: 'ia', 
        texto: dadosIA.resposta || dadosIA.texto || "Resposta recebida, mas formato inesperado.", 
        fontes: dadosIA.fontes || [] 
      };
      
      setMensagens(msgsAntigas => [...msgsAntigas, novaMensagemIA]);
    } catch (erro) {
      console.error("Erro detalhado na requisição:", erro);
      const mensagemErro = { 
        remetente: 'ia', 
        texto: "Ocorreu um erro de conexão com o motor vetorial. Verifique se o servidor local está operacional e se as políticas de CORS permitem a comunicação.", 
        fontes: [] 
      };
      setMensagens(msgsAntigas => [...msgsAntigas, mensagemErro]);
    } finally {
      setCarregando(false);
    }
  };

  const lidarComUpload = (evento) => {
    const arquivo = evento.target.files[0];
    if (arquivo) {
      const msgUpload = { remetente: 'ia', texto: `O arquivo PDF "${arquivo.name}" foi processado. O que gostaria de saber sobre as suas predisposições?` };
      setMensagens([...mensagens, msgUpload]);
    }
  };

return (
    <div className="flex flex-col items-center justify-center min-h-screen bg-white text-genera-roxo p-4 font-sans">
      
      <div className="w-full max-w-4xl bg-white border border-gray-400 rounded-xl shadow-2xl overflow-hidden flex flex-col h-[85vh]">
        
        {/* Cabeçalho com Efeito de Sombra (Divisor) */}
        <div className="bg-white p-6 text-center border-b border-gray-300 flex flex-col items-center shadow-md relative z-10">
          <img 
            src={logoGenera} 
            alt="Genera Logo" 
            className="h-27 mb-3 object-contain"
          />
          <p className="text-sm font-medium text-genera-roxo/70 uppercase tracking-widest">
            Assistente Especializado
          </p>
        </div>
        
        {/* Área de Mensagens com Sombra Interna */}
        <div className="flex-1 p-6 overflow-y-auto bg-gray-1000 shadow-inner">
          {mensagens.length === 0 ? (
            <div className="text-center text-genera-roxo/50 mt-20 font-light text-lg">
              Faça o upload do seu laudo em PDF ou digite a sua dúvida clínica abaixo.
            </div>
          ) : (
            mensagens.map((msg, index) => (
              <div key={index} className={`mb-6 ${msg.remetente === 'paciente' ? 'text-right' : 'text-left'}`}>
                <div className={`inline-block p-4 rounded-2xl max-w-[80%] shadow-sm ${
                  msg.remetente === 'paciente' 
                    ? 'bg-genera-roxo text-white rounded-br-none' 
                    : 'bg-white border border-gray-200 text-genera-roxo rounded-bl-none'
                }`}>
                  <p className="leading-relaxed">{msg.texto}</p>
                  {msg.fontes && msg.fontes.length > 0 && (
                    <div className="mt-3 pt-3 border-t border-current/20 text-xs opacity-80 text-left">
                      <span className="font-bold">Fontes do laudo: </span>
                      {msg.fontes.map((fonte, i) => (
                        <span key={i} className="inline-block bg-gray-100 text-genera-roxo rounded px-2 py-0.5 mr-1 mb-1">
                          {fonte.painel} — {fonte.marcador} ({fonte.gene})
                        </span>
                      ))}
                    </div>
                  )}
                </div>
              </div>
            ))
          )}
          {carregando && (
            <div className="text-left mb-6">
              <p className="inline-block p-4 rounded-2xl rounded-bl-none bg-white border border-gray-200 text-genera-roxo text-sm italic shadow-sm">
                A processar os dados genéticos...
              </p>
            </div>
          )}
        </div>

        {/* Área de Input */}
        <div className="p-5 bg-white border-t border-gray-200 flex flex-col gap-4 relative z-10 shadow-[0_-4px_6px_-1px_rgba(0,0,0,0.05)]">
          
          <div className="flex justify-start">
            <label className="cursor-pointer border-2 border-genera-magenta text-genera-magenta hover:bg-genera-magenta hover:text-white font-medium py-2 px-6 rounded-full transition-all duration-300 flex items-center gap-2 shadow-sm">
              <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" strokeWidth={2} stroke="currentColor" className="w-5 h-5">
                <path strokeLinecap="round" strokeLinejoin="round" d="M18.375 12.739l-7.693 7.693a4.536 4.536 0 01-6.42-6.421l10.899-10.899m-7.828 7.828l-5.656 5.656a2.268 2.268 0 003.207 3.207l5.657-5.657m5.656-5.656l-3.182 3.182" />
              </svg>
              Anexar Laudo PDF
              <input type="file" accept=".pdf" className="hidden" onChange={lidarComUpload} />
            </label>
          </div>

          <div className="flex gap-3 items-center w-full">
            <input
              type="text"
              className="flex-1 border-2 border-gray-200 rounded-full p-4 focus:outline-none focus:border-genera-magenta text-genera-roxo placeholder-gray-400 bg-gray-50 transition-colors shadow-inner"
              placeholder="Digite sua dúvida clínica..."
              value={inputUsuario}
              onChange={(e) => setInputUsuario(e.target.value)}
              onKeyDown={(e) => e.key === 'Enter' && enviarMensagem()}
            />
            <button 
              className="bg-genera-magenta hover:bg-genera-magentahover text-white font-bold py-4 px-8 rounded-full transition-colors shadow-md flex items-center gap-2"
              onClick={enviarMensagem}
            >
              Enviar
              <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" strokeWidth={2} stroke="currentColor" className="w-5 h-5">
                <path strokeLinecap="round" strokeLinejoin="round" d="M6 12L3.269 3.126A59.768 59.768 0 0121.485 12 59.77 59.77 0 013.27 20.876L5.999 12zm0 0h7.5" />
              </svg>
            </button>
          </div>
          
        </div>
      </div>
      <p className="text-xs text-genera-roxo/60 mt-6 text-center px-4 max-w-2xl">
        Aviso de Segurança e Governança: Este assistente utiliza IA generativa para a estruturação de laudos. As informações não substituem um diagnóstico médico invasivo ou profissional.
      </p>
    </div>
  );
}

