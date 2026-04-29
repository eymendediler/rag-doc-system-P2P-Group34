import os
from google import genai  
from typing import List


class EmbedderService:
    """
    Google gemini-embedding-004 modeli ile metin vektörleştirme servisi.
    - embed_text()  → tek sorgu için (RETRIEVAL_QUERY)
    - embed_batch() → indexleme için toplu işlem (RETRIEVAL_DOCUMENT)
    """

    def __init__(self):
        api_key = os.getenv("GOOGLE_API_KEY")
        if not api_key:
            raise ValueError(
                "GOOGLE_API_KEY bulunamadı! Lütfen .env dosyanızı kontrol edin."
            )
        
        # Yeni SDK'da 'genai.configure' yerine Client kullanılır
        self.client = genai.Client(
            api_key=api_key,
            http_options={'api_version': 'v1beta'}
            )
        self.model = "models/gemini-embedding-001"

    def embed_text(self, text: str) -> List[float]:
        """
        Tek bir metni vektöre çevirir.
        Kullanım: kullanıcı soruları (RETRIEVAL_QUERY).
        """
        if not text or not text.strip():
            raise ValueError("Boş metin embed edilemez.")

        # Yeni SDK'da 'contents' kullanılır ve config içinde task_type belirtilir
        result = self.client.models.embed_content(
            model=self.model,
            contents=text,
            config={"task_type": "RETRIEVAL_QUERY"}
        )
        # Sonuç artık bir nesnedir, embeddings[0].values ile listeye erişilir
        return result.embeddings[0].values

    def embed_batch(self, texts: List[str]) -> List[List[float]]:
        """
        Birden fazla metni tek seferde vektöre çevirir.
        Kullanım: doküman chunk'larını indexlerken (RETRIEVAL_DOCUMENT).
        """
        if not texts:
            raise ValueError("Boş liste embed edilemez.")

        # Boş chunk'ları temizle
        texts = [t for t in texts if t and t.strip()]
        if not texts:
            raise ValueError("Tüm chunk'lar boş, embed edilecek içerik yok.")

        result = self.client.models.embed_content(
            model=self.model,
            contents=texts,
            config={"task_type": "RETRIEVAL_DOCUMENT"}
        )
        
        return [e.values for e in result.embeddings]