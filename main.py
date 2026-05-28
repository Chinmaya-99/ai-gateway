from fastapi import FastAPI

from app.api.routes.health import router as health_router
from app.api.routes.chat import router as chat_router
from app.api.routes.embeddings import router as embeddings_router
from app.api.routes.cache import router as cache_router

app = FastAPI(title="AI Gateway")

app.include_router(health_router, prefix="/health")
app.include_router(chat_router, prefix="/chat")
app.include_router(embeddings_router, prefix="/embeddings")
app.include_router(cache_router, prefix="/cache")

@app.get("/")
def root():
    return {"message": "AI Gateway is running"}
