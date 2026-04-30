import os
import json
from groq import AsyncGroq
from typing import List, Dict, AsyncGenerator

class LLMService:
    def __init__(self):
        api_key = os.getenv("GROQ_API_KEY")
        if not api_key:
            raise ValueError("GROQ_API_KEY bulunamadı! Lütfen .env dosyanızı kontrol edin.")
        
        self.client = AsyncGroq(api_key=api_key)
        self.model = "llama-3.1-8b-instant"

    async def generate_streaming_response(self, context_texts: List[str], messages: List[Dict[str, str]], sources: List[str] = None) -> AsyncGenerator[str, None]:
        # Eğer kaynaklar varsa, önce kaynak bilgisini içeren bir chunk gönderelim
        if sources:
            sources_data = {"type": "sources", "sources": sources}
            yield f"data: {json.dumps(sources_data)}\n\n"
            
        # Bağlamı string'e çevir
        context_str = "\n\n".join(context_texts) if context_texts else "İlgili doküman bulunamadı."
        
        # Sistem promptunu hazırla
        system_prompt = f"""
Sen yardımsever bir asistansın. Aşağıdaki bağlamı kullanarak kullanıcının sorusuna cevap ver. 
Bağlamda bulunmayan bilgileri uydurma. Eğer cevap bağlamda yoksa, bunu kibarca belirt.

BAĞLAM:
{context_str}
"""
        
        # API için mesajları formatla
        api_messages = [{"role": "system", "content": system_prompt}]
        for msg in messages:
            api_messages.append({"role": msg["role"], "content": msg["content"]})
            
        try:
            stream = await self.client.chat.completions.create(
                messages=api_messages,
                model=self.model,
                temperature=0.3,
                max_tokens=1024,
                stream=True,
            )
            
            async for chunk in stream:
                if chunk.choices and chunk.choices[0].delta.content:
                    data = {"type": "content", "content": chunk.choices[0].delta.content}
                    yield f"data: {json.dumps(data)}\n\n"
                    
            yield "data: [DONE]\n\n"
            
        except Exception as e:
            error_data = {"type": "error", "error": str(e)}
            yield f"data: {json.dumps(error_data)}\n\n"
