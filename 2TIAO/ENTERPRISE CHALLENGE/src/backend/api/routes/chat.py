from fastapi import APIRouter, HTTPException
from domain.schemas import ChatRequest, ChatResponse, FonteDado
from agents.medical_agent import app

router = APIRouter()

@router.post("/", response_model=ChatResponse)
async def chat_com_agente(request: ChatRequest):
    try:
        resultado = app.invoke({"question": request.mensagem})
        fontes = [
            FonteDado(
                painel=d.metadata.get("painel", "N/A"),
                marcador=d.metadata.get("caracteristica", "N/A"),
                gene=d.metadata.get("gene", "N/A"),
                conclusao_curta=d.metadata.get("conclusao_curta", "N/A")
            ) for d in resultado.get("context", [])
        ]
        return ChatResponse(resposta=resultado["answer"], fontes=fontes)
    except Exception as e:
        import traceback
        traceback.print_exc() 
        raise HTTPException(status_code=500, detail=str(e))