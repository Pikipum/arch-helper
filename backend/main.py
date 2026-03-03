from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel

from config import CORS_ORIGINS
from service import chat_stream

app = FastAPI(title="Arch Helper API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
    allow_methods=["*"],
    allow_headers=["*"],
)

class ChatRequest(BaseModel):
    message: str
    history: list[dict] = []

@app.post("/api/chat")
async def chat(req: ChatRequest):
    return StreamingResponse(
        chat_stream(req.message, req.history),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "X-Accel-Buffering": "no",
        },
    )

@app.get("/api/health")
async def health():
    from rag import vector_store
    count = vector_store._collection.count()
    return {"status": "ok", "chunks_in_db": count}