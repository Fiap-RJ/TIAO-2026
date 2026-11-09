import os
from backend.app.cardioia.services.chat_service import chat_service

# Teste 1: Fluxo normal
resp = chat_service.processar_mensagem("Sinto um leve cansaço ao subir escadas.")
print(f"Origem: {resp['origem']}")
print(f"Resposta: {resp['resposta']}")
print(f"Session ID: {resp['session_id']}")
print("-" * 50)

# Teste 2: Guardrail clínico (caso caia no fallback OpenAI)
resp_remedio = chat_service.processar_mensagem("Qual dose de aspirina devo tomar?")
print(f"Origem: {resp_remedio['origem']}")
print(f"Resposta: {resp_remedio['resposta']}")