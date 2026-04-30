from fastapi import APIRouter, UploadFile, File, HTTPException
import uuid
from app.services.document_processor import DocumentProcessor
from app.services.chunker import TextChunker
from app.services.embedder import EmbedderService
from app.services.vector_store import VectorStoreService
from app.models.schemas import DocumentUploadResponse

router = APIRouter()

processor = DocumentProcessor()
chunker = TextChunker()

embedder_service = None
vector_store = None

def get_services():
    global embedder_service, vector_store
    if embedder_service is None:
        embedder_service = EmbedderService()
    if vector_store is None:
        vector_store = VectorStoreService()
    return embedder_service, vector_store


@router.post("/upload", response_model=DocumentUploadResponse)
async def upload_document(file: UploadFile = File(...)):
    try:
        embedder, vstore = get_services()
    except Exception as e:
         raise HTTPException(status_code=500, detail=f"Servis başlatma hatası: {str(e)}")

    try:
        # 1. Text çıkar
        text = await processor.extract_text(file)

        # 2. Chunk'lara böl
        chunks = chunker.chunk_text(text)
        
        if not chunks:
             raise ValueError("Dokümandan anlamlı metin çıkarılamadı.")

        # 3. Chunk'ları embed et
        embeddings = embedder.embed_batch(chunks)
        
        # 4. Vektör veritabanına kaydet
        doc_id = file.filename
        vstore.add_to_index(
            doc_id=doc_id,
            chunks=chunks,
            embeddings=embeddings,
            metadata={"filename": file.filename}
        )

        return {
            "filename": file.filename,
            "num_chunks": len(chunks),
            "chunks_preview": chunks[:3]
        }

    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))