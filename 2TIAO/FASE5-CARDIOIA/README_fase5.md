# FIAP - Faculdade de Informática e Administração Paulista

<p align="center">
<a href= "https://www.fiap.com.br/"><img src="assets/logo-fiap.png" alt="FIAP - Faculdade de Informática e Admnistração Paulista" border="0" width=40% height=40%></a>
</p>

<br>

# CardioIA: A Nova Era da Cardiologia Inteligente

## Nome do grupo

## 👨‍🎓 Integrantes: 
- <a href="https://www.linkedin.com/in/michaelrodriguess/">Michael Rodrigues</a>
- <a href="https://www.linkedin.com/in/arthur-alentejo/">Arthur Alentejo</a>
- <a href="https://www.linkedin.com/in/nathalia-vasconcelos-18a390292/">Nathalia Vasconcelos</a> 

## 👩‍🏫 Professores:
### Tutor(a) 
- <a href="#">Caique (CaiqueFiap-2026)</a>
### Coordenador(a)
- <a href="https://www.linkedin.com/in/andregodoichiovato/">André Godói</a>

## 📜 Descrição

O CardioIA é um ecossistema inteligente voltado à cardiologia moderna digital. Nesta quinta fase do projeto, consolidamos a integração de ponta a ponta desenvolvendo um Assistente Cardiológico Conversacional acoplado a uma interface web interativa em Flask.

O assistente foi desenhado para atuar na triagem e no esclarecimento preventivo de pacientes sobre sintomas e cuidados cardiovasculares. A camada de inteligência opera sobre o serviço cognitivo em nuvem IBM Watson Assistant (NLU/árvore de diálogo), consumido através de um backend estruturado em Python e servido visualmente em uma aplicação web responsiva.

### 🚀 Entregas da Fase 5 - Assistente Cardiológico Inteligente

1. Integração Cognitiva (IBM Watson Assistant)
Configuração do assistente cognitivo na IBM Cloud com foco em intenções, entidades médicas e árvore de diálogo estruturada para triagem cardiovascular.

Orquestração de sessões de diálogo com extração e contextualização de respostas do usuário.

2. Backend e API em Flask
Implementação de rotas REST para recepção de mensagens do usuário (POST /api/chat) e renderização da interface web (GET /).

Gerenciamento de credenciais e parâmetros de conexão via variáveis de ambiente com tratamento de erros de comunicação[cite: 1, 15].

3. Interface Web Interativa (Front-End)
Layout de chat responsivo construído para simular o atendimento digital humanizado com feedback instantâneo.

## 📁 Estrutura de Pastas do Projeto

O repositório está organizado de forma clara e padronizada seguindo boas práticas de governança técnica:

```
cardioIA-fase5/
├── assets/                  # Identidade visual e imagens de documentação
├── document/                # Relatório técnico e documentações da Fase 5
├── src/                     # Código-fonte da aplicação
│   ├── templates/           # Arquivos de visualização HTML
│   │   └── index.html
│   └── backend.py           # Aplicação Flask e integração com IBM Watson
├── .env.example             # Modelo das variáveis de ambiente necessárias
├── .gitignore               # Arquivos ignorados pelo Git (inclui o .env)
├── requirements.txt         # Dependências do projeto com versões fixadas
└── README.md                # Guia geral de configuração e execução

```

## 🔧 Como executar o código

Pré-requisitos:
- Python 3.10 ou superior.
- Acesso à internet e conta ativa na IBM Cloud com uma instância do Watson Assistant provisionada[cite: 8, 9].

1. Clonar o repositório e preparar o ambiente virtual

git clone 

cd cardioIA-fase5

- Criar o ambiente virtual

python -m venv .venv

- Ativar o ambiente virtual

No Windows (PowerShell):
.\.venv\Scripts\Activate.ps1

No Linux/macOS:
source .venv/bin/activate

2. Instalar as dependências do projeto

pip install -r requirements.txt

⚠️ Nota Crítica sobre a Biblioteca ibm-watson:

O projeto adota estritamente a versão ibm-watson==5.3.1. As versões 11.x+ mais recentes do SDK da IBM alteraram a nomenclatura dos métodos para environment_id e introduziram requisitos obrigatórios de payload (user_id), que geram incompatibilidades com o fluxo tradicional da API V2 do Watson. Não execute atualizações (upgrade) desta biblioteca sem validar as rotas no backend.py.

3. Configurar as variáveis de ambiente

Por diretrizes de segurança da informação, credenciais de nuvem não são enviadas ao repositório. Utilize o arquivo de exemplo para configurar o seu ambiente local

- Copie o arquivo modelo gerando o .env definitivo:

No Windows (CMD/PowerShell):

copy .env.example .env

No Linux/macOS:

cp .env.example .env

- Abra o arquivo .env na raiz do projeto e informe as chaves obtidas na IBM Cloud
WA_API_KEY=sua_api_key_ibm_aqui
WA_URL=https://api.us-south.assistant.watson.cloud.ibm.com
WA_ASSISTANT_ID=seu_assistant_id_aqui
FLASK_SECRET_KEY=sua_chave_secreta_flask_aqui

4. Executar a aplicação
Com o ambiente ativado e as variáveis configuradas, inicie o servidor local:

python src/backend.py

Abra o navegador no endereço indicado pelo Flask (por padrão, [http://127.0.0.1:5000](http://127.0.0.1:5000)) para interagir com o assistente em tempo real.



🗃 Histórico de Lançamentos





📋 Licença

<img style="height:22px!important;margin-left:3px;vertical-align:text-bottom;" src="https://mirrors.creativecommons.org/presskit/icons/cc.svg?ref=chooser-v1"><img style="height:22px!important;margin-left:3px;vertical-align:text-bottom;" src="https://mirrors.creativecommons.org/presskit/icons/by.svg?ref=chooser-v1"><p xmlns:cc="http://creativecommons.org/ns#" xmlns:dct="http://purl.org/dc/terms/"><a property="dct:title" rel="cc:attributionURL" href="https://github.com/agodoi/template">MODELO GIT FIAP</a> por <a rel="cc:attributionURL dct:creator" property="cc:attributionName" href="https://fiap.com.br">Fiap</a> está licenciado sobre <a href="http://creativecommons.org/licenses/by/4.0/?ref=chooser-v1" target="_blank" rel="license noopener noreferrer" style="display:inline-block;">Attribution 4.0 International</a>.</p>