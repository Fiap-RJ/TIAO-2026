const form = document.getElementById('chat-form');
const input = document.getElementById('user-input');
const button = document.getElementById('send-button');
const chatLog = document.getElementById('chat-log');

/**
 * Cria e insere um balão de mensagem no histórico.
 * Usa `textContent` (nunca `innerHTML`) para o texto do usuário/bot,
 * evitando que qualquer marcação digitada seja interpretada como HTML.
 */
function criarBalao(remetente, texto, classes) {
    const balao = document.createElement('div');
    balao.className = `message ${classes}`;

    const nome = document.createElement('span');
    nome.className = 'message-sender';
    nome.textContent = remetente;

    const corpo = document.createElement('p');
    corpo.className = 'message-text';
    corpo.textContent = texto;

    balao.append(nome, corpo);
    chatLog.appendChild(balao);
    chatLog.scrollTop = chatLog.scrollHeight;
    return balao;
}

function mostrarDigitando() {
    const balao = document.createElement('div');
    balao.className = 'message bot typing';
    balao.id = 'typing-indicator';
    balao.setAttribute('aria-label', 'CardioIA está digitando');
    for (let i = 0; i < 3; i += 1) {
        const ponto = document.createElement('span');
        ponto.className = 'dot';
        balao.appendChild(ponto);
    }
    chatLog.appendChild(balao);
    chatLog.scrollTop = chatLog.scrollHeight;
}

function removerDigitando() {
    document.getElementById('typing-indicator')?.remove();
}

function definirCarregando(carregando) {
    input.disabled = carregando;
    button.disabled = carregando;
    button.textContent = carregando ? 'Enviando...' : 'Enviar';
}

async function enviarMensagem(texto) {
    criarBalao('Você', texto, 'user');
    definirCarregando(true);
    mostrarDigitando();

    try {
        const resposta = await fetch('/api/chat', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ message: texto }),
        });

        let dados = null;
        try {
            dados = await resposta.json();
        } catch {
            dados = null;
        }

        removerDigitando();

        if (dados && dados.response) {
            criarBalao('CardioIA', dados.response, resposta.ok ? 'bot' : 'bot error');
        } else {
            criarBalao('CardioIA', 'Desculpe, ocorreu um erro de conexão.', 'bot error');
        }
    } catch (erro) {
        console.error('Erro na API:', erro);
        removerDigitando();
        criarBalao(
            'CardioIA',
            'O servidor não está respondendo. Tente novamente em instantes.',
            'bot error',
        );
    } finally {
        definirCarregando(false);
        input.focus();
    }
}

form.addEventListener('submit', (evento) => {
    evento.preventDefault();
    const texto = input.value.trim();
    if (!texto) return;
    input.value = '';
    enviarMensagem(texto);
});

window.addEventListener('DOMContentLoaded', () => input.focus());
