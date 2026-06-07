import { useState } from 'react';
import { Send, Bot, User, Loader2 } from 'lucide-react';
import axios from 'axios'; // Biblioteca para fazer a requisição HTTP para a API do Michael

export function ChatOrbital() {
  const [input, setInput] = useState('');
  const [isLoading, setIsLoading] = useState(false); // Novo estado para o "Pensando..."
  
  // Estado que guarda a lista de mensagens
  const [mensagens, setMensagens] = useState([
    { role: 'ia', content: 'Olá! Sou o agente Orbital RAG. Como posso ajudar com os dados espaciais hoje?' }
  ]);

  // Função que faz a mágica acontecer
  const enviarMensagem = async () => {
    // Se o input estiver vazio, não faz nada
    if (!input.trim()) return;

    // 1. Cria a mensagem do usuário e coloca na tela instantaneamente
    const novaMensagemUsuario = { role: 'user', content: input };
    
    // O React exige que criemos um novo array copiando as mensagens antigas (...prev)
    setMensagens((prev) => [...prev, novaMensagemUsuario]);
    
    // Limpa a caixa de texto e ativa o ícone de carregamento
    setInput('');
    setIsLoading(true); 

    try {
      // 2. Dispara a pergunta para o backend do Michael
      const response = await axios.post('http://localhost:3000/api/chat', {
        message: novaMensagemUsuario.content
      });

      // 3. Pega a resposta do JSON da API e coloca na tela
      const dadosIA = response.data;
      const novaMensagemIA = { 
        role: 'ia', 
        content: dadosIA.reply, 
        fontes: dadosIA.source_data 
      };
      
      setMensagens((prev) => [...prev, novaMensagemIA]);

    } catch (error) {
      console.error("Erro ao conectar com a API:", error);
      // Caso o backend do Michael esteja desligado, exibe uma mensagem de erro chique
      setMensagens((prev) => [...prev, { role: 'ia', content: '⚠️ Alerta: Perda de comunicação com os servidores orbitais (Backend fora do ar).' }]);
    } finally {
      // Desativa o ícone de carregamento, quer tenha dado certo ou errado
      setIsLoading(false);
    }
  };

  // Função para enviar apertando a tecla "Enter"
  const handleKeyPress = (e) => {
    if (e.key === 'Enter') {
      enviarMensagem();
    }
  };

  return (
    <div style={{ padding: '20px', maxWidth: '800px', margin: '0 auto' }}>
      <h2>Comando Interativo (RAG)</h2>
      
      {/* Área das Mensagens */}
      <div style={{ border: '1px solid #ccc', borderRadius: '8px', height: '400px', overflowY: 'auto', padding: '15px', marginBottom: '20px', backgroundColor: '#f9f9f9' }}>
        
        {mensagens.map((msg, index) => (
          <div key={index} style={{ marginBottom: '15px', display: 'flex', alignItems: 'flex-start', gap: '10px' }}>
            {msg.role === 'ia' ? <Bot color="blue" /> : <User color="green" />}
            <div style={{ backgroundColor: msg.role === 'ia' ? '#e3f2fd' : '#e8f5e9', padding: '10px', borderRadius: '8px', flex: 1 }}>
              <p style={{ margin: 0 }}>{msg.content}</p>
              
              {/* Se a IA retornou fontes (source_data), nós as renderizamos como pequenas "tags" */}
              {msg.fontes && msg.fontes.length > 0 && (
                <div style={{ marginTop: '10px', fontSize: '12px', color: '#555' }}>
                  <strong>Fontes analisadas: </strong>
                  {msg.fontes.map((fonte, i) => (
                    <span key={i} style={{ backgroundColor: '#ccc', padding: '3px 6px', borderRadius: '4px', marginRight: '5px' }}>
                      {fonte}
                    </span>
                  ))}
                </div>
              )}
            </div>
          </div>
        ))}

        {/* Efeito visual enquanto a API está "pensando" */}
        {isLoading && (
          <div style={{ display: 'flex', alignItems: 'center', gap: '10px', color: '#555' }}>
            <Bot color="gray" />
            <div style={{ padding: '10px', fontStyle: 'italic' }}>
              <Loader2 className="animate-spin" size={16} style={{ display: 'inline', marginRight: '5px' }} />
              Consultando base orbital...
            </div>
          </div>
        )}

      </div>

      {/* Área de Digitação */}
      <div style={{ display: 'flex', gap: '10px' }}>
        <input 
          type="text" 
          placeholder="Ex: Quais asteroides oferecem risco hoje?"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={handleKeyPress}
          disabled={isLoading} // Desabilita o input enquanto a IA pensa
          style={{ flex: 1, padding: '10px', borderRadius: '8px', border: '1px solid #ccc' }}
        />
        <button 
          onClick={enviarMensagem} 
          disabled={isLoading} // Desabilita o botão enquanto a IA pensa
          style={{ padding: '10px 20px', backgroundColor: isLoading ? '#ccc' : '#0d47a1', color: 'white', border: 'none', borderRadius: '8px', cursor: isLoading ? 'not-allowed' : 'pointer', display: 'flex', alignItems: 'center', gap: '5px' }}
        >
          Enviar <Send size={16} />
        </button>
      </div>
    </div>
  );
}