import os
from pathlib import Path
from dotenv import load_dotenv

from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_community.vectorstores import FAISS

load_dotenv()

CURRENT_DIR = Path(__file__).parent
BACKEND_DIR = CURRENT_DIR.parent
FAISS_INDEX_PATH = BACKEND_DIR / "faiss_index"

def testar_busca_semantica():
    print("1. Ligando o motor de Embeddings do Google...")
    embeddings = GoogleGenerativeAIEmbeddings(
        model="models/gemini-embedding-001",
        google_api_key=os.getenv("GOOGLE_API_KEY")
    )
    
    print(f"2. Carregando o banco vetorial de: {FAISS_INDEX_PATH}")
    # para carregar arquivos .pkl locais. É seguro porque nós mesmos geramos o arquivo.
    vector_store = FAISS.load_local(
        str(FAISS_INDEX_PATH), 
        embeddings,
        allow_dangerous_deserialization=True
    )
    
    # Transformamos o banco em um "Retriever", pedindo para trazer os 2 melhores resultados (k=2)
    retriever = vector_store.as_retriever(search_kwargs={"k": 2})
    
    # Simulando a pergunta do usuário
    pergunta = "O laudo aponta alguma mutação relacionada a risco cardíaco ou problemas no coração?"
    
    print(f"\n🗣️ Pergunta Simulada: '{pergunta}'")
    print("⏳ Buscando no laudo...\n")
    
    resultados = retriever.invoke(pergunta)
    
    if not resultados:
        print("Nenhum contexto médico encontrado.")
        return

    print("✅ Resultados Encontrados (Contexto para o Agente):\n")
    for i, doc in enumerate(resultados, 1):
        print(f"--- Documento {i} ---")
        print(f"Trecho Exato: {doc.page_content}")
        print(f"Metadados: {doc.metadata}")
        print("-" * 20 + "\n")

if __name__ == "__main__":
    testar_busca_semantica()