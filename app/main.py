from dotenv import load_dotenv
load_dotenv()
from fastapi import FastAPI
from app.api.routes import documents,chat

app = FastAPI(title="RAG Document System")

app.include_router(documents.router)
app.include_router(chat.router)


@app.get("/")
def root():
    return {"status": "ok", "message": "API is running 🚀"}