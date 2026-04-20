from fastapi import FastAPI
from app.api.routes import documents

app = FastAPI(title="RAG Document System")

app.include_router(documents.router)


@app.get("/")
def root():
    return {"status": "ok", "message": "API is running 🚀"}