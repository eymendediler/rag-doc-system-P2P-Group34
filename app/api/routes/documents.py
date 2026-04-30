from fastapi import APIRouter, UploadFile, File, HTTPException
from app.services.document_processor import DocumentProcessor
from app.services.chunker import TextChunker

router = APIRouter()

processor = DocumentProcessor()
chunker = TextChunker()


@router.post("/upload")
async def upload_document(file: UploadFile = File(...)):
    try:
        # 1. Text çıkar
        text = await processor.extract_text(file)

        # 2. Chunk'lara böl
        chunks = chunker.chunk_text(text)

        return {
            "filename": file.filename,
            "num_chunks": len(chunks),
            "chunks_preview": chunks[:3]  # sadece ilk 3 chunk
        }

    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))