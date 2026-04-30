import { useState } from "react";
import "./App.css";

export default function App() {
  const [messages, setMessages] = useState([
    {
      role: "assistant",
      content:
        "Merhaba! Dokümanlarını yükle, sonra PDF, DOCX veya TXT içerikleri hakkında bana soru sorabilirsin ✨",
    },
  ]);

  const [input, setInput] = useState("");
  const [files, setFiles] = useState([]);
  const [docIds, setDocIds] = useState([]);
  const [isUploading, setIsUploading] = useState(false);
  const [isTyping, setIsTyping] = useState(false);

  const handleFiles = async (e) => {
    const selectedFiles = Array.from(e.target.files);
    setFiles((prev) => [...prev, ...selectedFiles]);
    setIsUploading(true);

    for (const file of selectedFiles) {
      const formData = new FormData();
      formData.append("file", file);
      
      try {
        const res = await fetch("http://localhost:8000/upload", {
          method: "POST",
          body: formData,
        });
        const data = await res.json();
        if (data.filename) {
           setDocIds(prev => {
             if (!prev.includes(data.filename)) {
                return [...prev, data.filename];
             }
             return prev;
           });
        }
      } catch (err) {
        console.error("Upload error:", err);
      }
    }
    setIsUploading(false);
  };

  const sendMessage = async () => {
    if (!input.trim()) return;

    const question = input;
    setInput("");

    setMessages((prev) => [
      ...prev,
      { role: "user", content: question },
      { role: "assistant", content: "", sources: [] },
    ]);
    setIsTyping(true);
    
    try {
      const currentMessages = [...messages, { role: "user", content: question }];
      
      const response = await fetch("http://localhost:8000/chat", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
           messages: currentMessages.map(m => ({ role: m.role, content: m.content })),
           doc_ids: docIds.length > 0 ? docIds : undefined
        })
      });
      
      const reader = response.body.getReader();
      const decoder = new TextDecoder("utf-8");
      
      while (true) {
        const { done, value } = await reader.read();
        if (done) break;
        
        const chunkStr = decoder.decode(value, { stream: true });
        const lines = chunkStr.split("\n");
        
        for (const line of lines) {
          if (line.startsWith("data: ")) {
            const dataStr = line.replace("data: ", "");
            if (dataStr === "[DONE]") break;
            
            try {
              const data = JSON.parse(dataStr);
              if (data.type === "sources") {
                 setMessages((prev) => {
                    const newMessages = [...prev];
                    const lastIdx = newMessages.length - 1;
                    newMessages[lastIdx] = { ...newMessages[lastIdx], sources: data.sources };
                    return newMessages;
                 });
              } else if (data.type === "content") {
                 setMessages((prev) => {
                    const newMessages = [...prev];
                    const lastIdx = newMessages.length - 1;
                    newMessages[lastIdx] = { ...newMessages[lastIdx], content: newMessages[lastIdx].content + data.content };
                    return newMessages;
                 });
              } else if (data.type === "error") {
                 console.error("LLM Error:", data.error);
                 setMessages((prev) => {
                    const newMessages = [...prev];
                    const lastIdx = newMessages.length - 1;
                    newMessages[lastIdx] = { ...newMessages[lastIdx], content: newMessages[lastIdx].content + "\n[Hata oluştu]" };
                    return newMessages;
                 });
              }
            } catch (e) {
               console.error("JSON parse error:", e);
            }
          }
        }
      }
      
    } catch (err) {
       console.error("Chat error:", err);
       setMessages(prev => {
          const newMessages = [...prev];
          newMessages[newMessages.length - 1].content = "Bir hata oluştu. Lütfen tekrar deneyin.";
          return newMessages;
       });
    } finally {
       setIsTyping(false);
    }
  };

  return (
    <div className="app">
      <aside className="sidebar">
        <div className="brand">
          <div className="yzta-logo">
            <div className="roof"></div>
            <div className="bars">
              <span className="red"></span>
              <span className="yellow"></span>
              <span className="green"></span>
            </div>
            <div className="base"></div>
          </div>

          <div>
            <h2>YZTA-P2P-G34</h2>
            <p>DocMind AI Workspace</p>
          </div>
        </div>

        <div className="side-highlight">
          <strong>AI hazır 🤖</strong>
          <p>Yükle, sor, özetle, kaynakları gör.</p>
        </div>

        <div className="panel p2p-card">
          <h3>🤝 P2P Amacı</h3>
          <p>Birlikte öğrenme, geliştirme ve paylaşım odaklı süreç.</p>
        </div>

        <nav className="menu">
          <button className="active">💬 Sohbet</button>
          <button>📄 Dokümanlarım</button>
          <button>✨ Özetler</button>
        </nav>

        <div className="panel">
          <h3>📁 Doküman Yükle</h3>
          <p>PDF, DOCX, DOC veya TXT dosyalarını yükle.</p>

          <label className="upload-box">
            <input
              type="file"
              multiple
              accept=".pdf,.doc,.docx,.txt"
              onChange={handleFiles}
            />
            <span>＋ Dosya Seç</span>
            <small>Birden fazla dosya desteklenir</small>
          </label>
        </div>

        <div className="panel files">
          <h3>Yüklenen Dokümanlar</h3>

          {files.length === 0 ? (
            <div className="empty-state">
              <span>🗂️</span>
              <p>Henüz dosya yüklenmedi.</p>
            </div>
          ) : (
            files.map((file, i) => (
              <div className="file" key={i}>
                <div className="file-badge">
                  {file.name.split(".").pop().toUpperCase()}
                </div>
                <div>
                  <strong>{file.name}</strong>
                  <small>{(file.size / 1024 / 1024).toFixed(2)} MB</small>
                </div>
                <span className="dot"></span>
              </div>
            ))
          )}
        </div>

        <div className="user">
          <div className="avatar">G34</div>
          <div>
            <strong>Group 34</strong>
            <p>YZTA-P2P Challenge</p>
          </div>
        </div>
      </aside>

      <main className="main">
        <section className="hero">
          <div className="hero-content">
            <div className="top-line">
              <span className="badge">RAG Powered Assistant</span>
              <span className="live-pill">
                <span></span> Live API
              </span>
            </div>

            <h1>
              Dokümanlarınla <span>Sohbet Et</span>
            </h1>

            <p>
              Belgelerini yükle, sorular sor, özet çıkar ve kaynaklı cevaplar al.
            </p>
          </div>

          <div className="floating-docs">
            <div className="float-doc pdf">PDF</div>
            <div className="float-doc docx">DOCX</div>
            <div className="float-doc txt">TXT</div>
          </div>

          <label className="hero-upload">
            <input
              type="file"
              multiple
              accept=".pdf,.doc,.docx,.txt"
              onChange={handleFiles}
            />
            ＋ Doküman Yükle
          </label>
        </section>

        <section className="p2p-strip">
          <div>
            <span>🧠</span>
            <h4>Teknik Gelişim</h4>
            <p>LLM, RAG ve doküman işleme pratiği.</p>
          </div>
          <div>
            <span>🤝</span>
            <h4>Akran Değerlendirmesi</h4>
            <p>Ekipler birbirinin yaklaşımını görür.</p>
          </div>
          <div>
            <span>🌍</span>
            <h4>Topluluk Paylaşımı</h4>
            <p>Süreç ve çözümler paylaşılır.</p>
          </div>
        </section>

        <section className="stats">
          <div>
            <span>📚</span>
            <p>Toplam Doküman</p>
            <h3>{files.length}</h3>
          </div>
          <div>
            <span>💬</span>
            <p>Toplam Mesaj</p>
            <h3>{messages.length}</h3>
          </div>
          <div>
            <span>✨</span>
            <p>Vektör Veritabanı</p>
            <h3>{docIds.length} doc</h3>
          </div>
          <div>
            <span>⚡</span>
            <p>Durum</p>
            <h3>{isUploading ? "Yükleniyor..." : isTyping ? "Yazıyor..." : "Hazır"}</h3>
          </div>
        </section>

        <section className="chat">
          {messages.map((msg, i) => (
            <div key={i} className={`message ${msg.role}`}>
              <div className="bubble">
                <strong>{msg.role === "user" ? "Sen" : "🤖 DocMind"}</strong>
                <p>{msg.content}</p>

                {msg.role === "assistant" && i > 0 && msg.sources && msg.sources.length > 0 && (
                  <div className="sources">
                    <b>Kaynaklar</b>
                    {msg.sources.map((src, idx) => (
                       <span key={idx}>📌 {src}</span>
                    ))}
                  </div>
                )}
              </div>
            </div>
          ))}
        </section>

        <div className="quick-prompts">
          {[
            "RAG nedir?",
            "Bu dokümanı özetle",
            "Teknik beklentiler neler?",
            "P2P sürecini açıkla",
            "Projeyi nasıl sunarım?",
          ].map((text) => (
            <button key={text} onClick={() => setInput(text)}>
              {text}
            </button>
          ))}
        </div>

        <footer className="composer">
          <input
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={(e) => e.key === "Enter" && sendMessage()}
            placeholder="Dokümanlarınla ilgili bir soru sor..."
          />
          <button onClick={sendMessage}>Gönder 🚀</button>
        </footer>
      </main>
    </div>
  );
}