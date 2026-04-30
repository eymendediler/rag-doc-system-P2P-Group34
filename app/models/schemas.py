from pydantic import BaseModel
from typing import List, Optional

class Message(BaseModel):
    role: str
    content: str

class ChatRequest(BaseModel):
    messages: List[Message]
    doc_ids: Optional[List[str]] = None

class DocumentUploadResponse(BaseModel):
    filename: str
    num_chunks: int
    chunks_preview: List[str]
