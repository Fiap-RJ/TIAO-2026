import json
import os
from pathlib import Path
from dotenv import load_dotenv
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_core.documents import Document
from core.config import settings

load_dotenv()

CURRENT_DIR = Path(__file__).parent
BACKEND_DIR = CURRENT_DIR.parent
PROJECT_ROOT = BACKEND_DIR.parent.parent
JSON_PATH = PROJECT_ROOT / "proposta_estrutura_de_dados.json"
FAISS_INDEX_PATH = BACKEND_DIR / "faiss_index"

def carregar_dados_json() -> list[Document]:
    with open(JSON_PATH, "r", encoding="utf-8") as f:
        dados = json.load(f)
    
    documentos = []
    for painel in dados.get("paineis_geneticos", []):
        for resultado in painel.get("resultados", []):
            conteudo = f"Característica: {resultado['caracteristica']}. Conclusão: {resultado['conclusao_curta']}. Explicação: {resultado['explicacao_detalhada']}"
            metadados = {
                "painel": painel.get("nome_painel"),
                "caracteristica": resultado.get("caracteristica"),
                "gene": resultado.get("dados_tecnicos", {}).get("gene", "N/A"),
                "conclusao_curta": resultado.get("conclusao_curta")
            }
            documentos.append(Document(page_content=conteudo, metadata=metadados))
    return documentos

def criar_e_salvar_banco_vetorial():
    documentos = carregar_dados_json()
    embeddings = GoogleGenerativeAIEmbeddings(model=settings.EMBEDDING_MODEL, google_api_key=settings.GOOGLE_API_KEY, task_type="RETRIEVAL_DOCUMENT")
    vector_store = FAISS.from_documents(documentos, embeddings)
    vector_store.save_local(str(FAISS_INDEX_PATH))
    print("✅ Banco Vetorial salvo.")

def load_vector_store():
    embeddings = GoogleGenerativeAIEmbeddings(
        model=settings.EMBEDDING_MODEL,
        google_api_key=settings.GOOGLE_API_KEY
    )
    return FAISS.load_local(
        str(FAISS_INDEX_PATH), 
        embeddings, 
        allow_dangerous_deserialization=True
    )

if __name__ == "__main__":
    criar_e_salvar_banco_vetorial()