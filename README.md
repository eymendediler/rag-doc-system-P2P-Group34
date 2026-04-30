# 📚 DocMind AI Workspace (RAG Document System)

DocMind, belgelerinizi (PDF, DOCX, TXT) yükleyip, bu belgelerin içeriğine dair doğal dilde sorular sorabileceğiniz **RAG (Retrieval-Augmented Generation)** tabanlı akıllı bir sohbet sistemidir. YZTA P2P (Group 34) ekibi tarafından geliştirilmiştir.

## ✨ Özellikler

- **Çoklu Doküman Yükleme:** PDF, DOCX ve TXT dosyalarını sisteme yükleme ve metin çıkarma.
- **Akıllı Bölütleme (Chunking) & Embedding:** Belgeler, anlamlı parçalara bölünerek (chunking) Google Gemini Embedding modeli ile vektörel uzaya aktarılır.
- **Vektör Veritabanı:** Çıkarılan vektörler yerel **ChromaDB** veritabanında saklanır ve hızlı anlamsal (semantik) arama imkanı sunar.
- **Gerçek Zamanlı Sohbet (Streaming):** Groq API (Llama 3.1 8B) kullanılarak modelden gelen cevaplar hiç beklemeden harf harf (streaming) arayüze aktarılır.
- **Kaynak Gösterimi:** Yapay zeka cevap verirken, cevabın hangi belgeden alındığını kaynak olarak gösterir.
- **Modern Arayüz:** React ve Vite ile geliştirilmiş şık, dinamik ve karanlık mod odaklı modern kullanıcı arayüzü.

## 🛠️ Kullanılan Teknolojiler

- **Frontend:** React, Vite, Vanilla CSS, SSE (Server-Sent Events)
- **Backend:** Python, FastAPI, Uvicorn, Pydantic
- **AI & RAG:** Groq API (LLM), Google GenAI (Embedding), ChromaDB (Vector Store), PyMuPDF / python-docx (Doküman Okuma)

---

## 🚀 Kurulum ve Çalıştırma

### 1. Ön Koşullar
Projeyi bilgisayarınızda lokal olarak çalıştırmak için **Python (3.9+)** ve **Node.js** yüklü olmalıdır.

### 2. Projeyi Klonlayın
```bash
git clone https://github.com/eymendediler/rag-doc-system-P2P-Group34.git
cd rag-doc-system-P2P-Group34
```

### 3. API Anahtarlarını Ayarlama (.env)
Projenin ana dizininde `.env` isimli bir dosya oluşturun ve içerisine API anahtarlarınızı ekleyin (Örnek şablon için `.env.example` dosyasına bakabilirsiniz):
```env
GROQ_API_KEY=gsk_sizin_groq_api_anahtariniz
GOOGLE_API_KEY=AIzaSy_sizin_google_api_anahtariniz
```
*(Eğer bu anahtarlara sahip değilseniz Groq Console ve Google AI Studio üzerinden ücretsiz alabilirsiniz).*

### 4. Backend'i Başlatma (FastAPI)
Terminalde ana dizindeyken:
```bash
# 1. Gerekli kütüphaneleri yükleyin
pip install -r requirements.txt

# 2. Sunucuyu başlatın
uvicorn app.main:app --reload
```
*Backend sunucusu `http://localhost:8000` adresinde çalışacaktır.*

### 5. Frontend'i Başlatma (React/Vite)
Ayrı bir terminal sekmesi açın ve ana dizindeyken:
```bash
# 1. Paketleri yükleyin
npm install

# 2. React sunucusunu başlatın
npm run dev
```
*Frontend arayüzü `http://localhost:5173` adresinde açılacaktır.*

---

## 👥 Ekip (P2P Group 34)
Bu proje **YZTA-P2P Challenge** kapsamında geliştirilmiş olup, birlikte öğrenme (peer-to-peer) ve yapay zeka (LLM & RAG) tekniklerinin pratikte uygulanmasına odaklanan bir çalışmadır.
