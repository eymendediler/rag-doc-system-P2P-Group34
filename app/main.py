from fastapi import FastAPI

app = FastAPI(title="RAG Document System")

@app.get("/")
def root():
    return {"status": "ok", "message": "API is running 🚀"}
