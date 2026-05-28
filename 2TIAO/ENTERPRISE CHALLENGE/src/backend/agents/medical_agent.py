from typing import TypedDict, List
from langchain_core.documents import Document
from langgraph.graph import StateGraph, END
from services.vector_store import load_vector_store
import requests
from core.config import settings

class AgentState(TypedDict):
    question: str
    context: List[Document]
    answer: str

def retrieve(state: AgentState):
    vector_store = load_vector_store()
    docs = vector_store.similarity_search(state["question"], k=2)
    return {"context": docs}

def generate(state: AgentState):
    docs_content = "\n\n".join([d.page_content for d in state["context"]])
    
    prompt = (
        "Você é um assistente virtual de Inteligência Artificial especializado na interpretação de laudos genéticos da Dasa.\n"
        "Seu papel é puramente informativo: traduzir os termos técnicos, genes e marcadores para uma linguagem clara e acessível ao paciente.\n\n"
        "Regras Críticas de Conduta:\n"
        "1. Você NÃO é um médico. Nunca dê um diagnóstico final, não minimize sintomas e nunca prescreva ou sugira tratamentos ou exames.\n"
        "2. Baseie-se EXCLUSIVAMENTE no contexto do laudo fornecido abaixo. Se o laudo não contiver a resposta, informe educadamente que o dado não consta no documento.\n"
        "3. Lembre o usuário de que mutações genéticas indicam PREDISPOSIÇÕES e RISCOS APENAS, e não uma certeza de desenvolvimento de condições.\n"
        "4. OBRIGATÓRIO: Toda resposta deve encerrar com um parágrafo claro reforçando a necessidade absoluta de consultar um médico geneticista ou especialista clínico para correlação dos dados com o histórico do paciente.\n\n"
        f"Contexto do Laudo Genético:\n{docs_content}\n\n"
        f"Pergunta do Paciente: {state['question']}\n\n"
        "Resposta do Assistente Dasa:"
    )
    
    # Pega a lista de modelos disponíveis para SUA chave
    url_list = f"https://generativelanguage.googleapis.com/v1/models?key={settings.GOOGLE_API_KEY}"
    response_list = requests.get(url_list)
    modelos = response_list.json().get('models', [])
    
    # Escolhe o primeiro modelo que suporta 'generateContent'
    model_id = next(m['name'] for m in modelos if 'generateContent' in m['supportedGenerationMethods'])
    
    print(f"DEBUG: Usando modelo detectado automaticamente: {model_id}")
    
    url_gen = f"https://generativelanguage.googleapis.com/v1/{model_id}:generateContent?key={settings.GOOGLE_API_KEY}"
    payload = {"contents": [{"parts": [{"text": prompt}]}]}
    
    response = requests.post(url_gen, json=payload)
    if response.status_code != 200:
        raise Exception(f"Erro na API {response.status_code}: {response.text}")
        
    answer = response.json()['candidates'][0]['content']['parts'][0]['text']
    return {"answer": answer}

workflow = StateGraph(AgentState)
workflow.add_node("retrieve", retrieve)
workflow.add_node("generate", generate)
workflow.set_entry_point("retrieve")
workflow.add_edge("retrieve", "generate")
workflow.add_edge("generate", END)

app = workflow.compile()