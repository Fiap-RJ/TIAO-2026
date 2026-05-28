import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent))

from agents.medical_agent import app

def run_test():
    print("🚀 Iniciando teste do LangGraph (Medical Agent)...")
    
    # Simula uma pergunta real
    inputs = {"question": "O laudo aponta risco cardíaco?"}
    
    print(f"🗣️ Pergunta: {inputs['question']}")
    print("⏳ Processando via RAG...\n")
    
    try:
        resultado = app.invoke(inputs)
        print("--- RESPOSTA DO AGENTE ---")
        print(resultado["answer"])
    except Exception as e:
        print(f"❌ Erro durante a execução: {e}")

if __name__ == "__main__":
    run_test()