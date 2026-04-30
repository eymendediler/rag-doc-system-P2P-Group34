import chromadb
import uuid
from typing import List, Optional, Dict
import logging

class VectorStoreService:
    def __init__(self):
        # Klasör yolunu belirlerken hata payını azaltmak için
        self.client = chromadb.PersistentClient(path="./chroma_db")
        self.collection = self.client.get_or_create_collection(
            name="document_collection",
            metadata={"hnsw:space": "cosine"}
        )
        self.logger = logging.getLogger(__name__)

    def add_to_index(
        self,
        doc_id: str,
        chunks: List[str],
        embeddings: List[List[float]],
        metadata: Dict
    ) -> None:
        if len(chunks) != len(embeddings):
            raise ValueError("Chunk ve Embedding sayıları uyumsuz!")

        try:
            # ÖNCE SİL: Aynı döküman ID'si varsa eski parçalar temizlensin (Hayalet chunk önleme)
            self.delete_document(doc_id)

            ids = [f"{doc_id}_{i}" for i in range(len(chunks))]
            
            # Metadata güvenliği: Kullanıcının gönderdiği metadata'yı temizle/hazırla
            clean_metadata = {k: v for k, v in metadata.items() if k != "source"}
            metadatas = [{"source": doc_id, **clean_metadata} for _ in chunks]

            self.collection.add(
                ids=ids,
                embeddings=embeddings,
                documents=chunks,
                metadatas=metadatas
            )
            print(f"✅ [VectorStore] {len(chunks)} parça başarıyla kaydedildi: {doc_id}")
        except Exception as e:
            self.logger.error(f"Kayıt sırasında hata: {e}")
            raise

    def search(
        self,
        query_embedding: List[float],
        top_k: int = 5,
        doc_ids: Optional[List[str]] = None
    ) -> Dict:
        """Sorgu yapar. Sonuçları daha okunaklı bir formatta dönebilirsin."""
        try:
            kwargs = {
                "query_embeddings": [query_embedding],
                "n_results": top_k,
                "include": ["documents", "metadatas", "distances"]
            }

            if doc_ids:
                if len(doc_ids) == 1:
                    kwargs["where"] = {"source": doc_ids[0]}
                else:
                    kwargs["where"] = {"source": {"$in": doc_ids}}

            return self.collection.query(**kwargs)
        except Exception as e:
            self.logger.error(f"Arama sırasında hata: {e}")
            return {"documents": [[]], "metadatas": [[]], "distances": [[]]}

    def delete_document(self, doc_id: str) -> None:
        """Dökümanı güvenli bir şekilde siler."""
        try:
            # Mevcut olup olmadığını kontrol etmeden silmek Chroma'da hata vermez
            self.collection.delete(where={"source": doc_id})
        except Exception as e:
            self.logger.warning(f"Silme işlemi başarısız (belki döküman yoktu): {e}")

    def list_documents(self) -> List[str]:
        """Büyük verilerde dikkatli kullanılmalı!"""
        try:
            # Sadece metadataları çek, tüm metinleri (documents) çekme! (Bellek dostu)
            results = self.collection.get(include=["metadatas"])
            if not results or not results['metadatas']:
                return []
            
            sources = {m.get("source") for m in results['metadatas'] if m}
            return list(sources)
        except Exception as e:
            self.logger.error(f"Liste çekilirken hata: {e}")
            return []