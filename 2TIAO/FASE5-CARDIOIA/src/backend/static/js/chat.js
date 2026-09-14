// Função para adicionar as mensagens na tela
function appendMessage(sender, text, className) {
    const chatLog = document.getElementById('chat-log');
    const messageDiv = document.createElement('div');
    messageDiv.className = `message ${className}`;
    messageDiv.innerHTML = `<span>${text}</span>`;
    chatLog.appendChild(messageDiv);
    chatLog.scrollTop = chatLog.scrollHeight;
}

// Função para enviar a mensagem via POST para o Flask usando fetch
async function sendMessage() {
    const inputField = document.getElementById('user-input');
    const userText = inputField.value.trim();
    if (userText === "") return;

    appendMessage('Você', userText, 'user');
    inputField.value = '';

    try {
        const response = await fetch('/api/chat', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ message: userText })
        });

        const data = await response.json();

        if (data.response) {
            appendMessage('CardioIA', data.response, 'bot');
        } else {
            appendMessage('Erro', 'Desculpe, ocorreu um erro de conexão.', 'bot');
        }
    } catch (error) {
        console.error('Erro na API:', error);
        appendMessage('Erro', 'O servidor não está respondendo.', 'bot');
    }
}

// Permite enviar apertando Enter
function handleKeyPress(event) {
    if (event.key === "Enter") {
        sendMessage();
    }
}
