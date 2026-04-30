from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse
from app.models.schemas import ChatRequest
from app.services.llm_service import LLMService
from app.services.embedder import EmbedderService
from app.services.vector_store import VectorStoreService

router = APIRouter()

# Lazy loading için (Uygulama kalkarken API key eksikse hemen hata vermesin diye)
llm_service = None
embedder_service = None
vector_store = None

def get_services():
    global llm_service, embedder_service, vector_store
    if llm_service is None:
        llm_service = LLMService()
    if embedder_service is None:
        embedder_service = EmbedderService()
    if vector_store is None:
        vector_store = VectorStoreService()
    return llm_service, embedder_service, vector_store

@router.post("/chat")
async def chat_endpoint(request: ChatRequest):
    if not request.messages:
        raise HTTPException(status_code=400, detail="Mesaj listesi boş olamaz.")
        
    try:
        llm, embedder, vstore = get_services()
    except Exception as e:
         raise HTTPException(status_code=500, detail=f"Servis başlatma hatası: {str(e)}")
         
    user_query = request.messages[-1].content
    
    # 1. Kullanıcı sorusunu vektöre çevir
    try:
        query_embedding = embedder.embed_text(user_query)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Embedding hatası: {str(e)}")
        
    # 2. ChromaDB'de benzer metinleri ara
    search_results = vstore.search(
        query_embedding=query_embedding,
        top_k=5,
        doc_ids=request.doc_ids
    )
    
    # 3. Sonuçlardan bağlam metinlerini ve kaynakları çıkart
    context_texts = []
    sources = []
    
    if search_results and "documents" in search_results and search_results["documents"]:
        if search_results["documents"][0]:
            context_texts = search_results["documents"][0]
            
    if search_results and "metadatas" in search_results and search_results["metadatas"]:
        if search_results["metadatas"][0]:
            for meta in search_results["metadatas"][0]:
                if meta and "source" in meta and meta["source"] not in sources:
                    sources.append(meta["source"])
            
    # LLM Servisi için mesaj formatını ayarla
    messages_dict = [{"role": msg.role, "content": msg.content} for msg in request.messages]
    
    # 4. SSE (Server-Sent Events) ile Streaming yanıtı dön
    return StreamingResponse(
        llm.generate_streaming_response(context_texts, messages_dict, sources),
        media_type="text/event-stream"
    )
