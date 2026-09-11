import os
from flask import Flask, request, jsonify, render_template, session
from ibm_watson import AssistantV2
from ibm_cloud_sdk_core.authenticators import IAMAuthenticator
from dotenv import load_dotenv

# Carrega as variáveis do arquivo .env
load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv("FLASK_SECRET_KEY", "chave_padrao_caso_nao_encontre")

# Configuração do SDK do Watson Assistant
WA_API_KEY = os.getenv("WA_API_KEY")
WA_URL = os.getenv("WA_URL")
WA_ASSISTANT_ID = os.getenv("WA_ASSISTANT_ID")

authenticator = IAMAuthenticator(WA_API_KEY)
assistant = AssistantV2(
    version="2021-06-14",
    authenticator=authenticator
)
assistant.set_service_url(WA_URL)

# Rota para exibir a interface HTML no navegador
@app.route('/')
def index():
    return render_template('index.html')

# Rota POST para comunicação com o front-end
@app.route('/api/chat', methods=['POST'])
def chat():
    user_msg = request.json.get('message', '')

    try:
        session_response = assistant.create_session(
            assistant_id=WA_ASSISTANT_ID
        ).get_result()
        session_id = session_response['session_id']

        response = assistant.message(
            assistant_id=WA_ASSISTANT_ID,
            session_id=session_id,
            input={
                'message_type': 'text',
                'text': user_msg
            }
        ).get_result()

        wa_text = response['output']['generic'][0]['text']
        return jsonify({"response": wa_text})

    except Exception as e:
        return jsonify({"response": f"⚠️ ERRO DO WATSON: {str(e)}"})

if __name__ == '__main__':
    app.run(debug=True)