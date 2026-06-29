from contextlib import asynccontextmanager

from fastapi import FastAPI

from ai_gateway.app.api.routes.health import router as health_router
from ai_gateway.app.api.routes.chat import router as chat_router
from ai_gateway.app.api.routes.embeddings import router as embeddings_router
from ai_gateway.app.api.routes.cache import router as cache_router
from ai_gateway.app.services.cache.cache_manager import CacheManager


@asynccontextmanager
async def lifespan(app: FastAPI):
    # ── Startup ────────────────────────────────────────────────────────
    app.state.cache_manager = await CacheManager.create()

    yield

    # ── Shutdown ───────────────────────────────────────────────────────
    await app.state.cache_manager.close()


app = FastAPI(title="AI Gateway", lifespan=lifespan)

app.include_router(health_router, prefix="/health")
app.include_router(chat_router, prefix="/chat")
app.include_router(embeddings_router, prefix="/embeddings")
app.include_router(cache_router, prefix="/cache")


@app.get("/")
async def root():
    return {"message": "AI Gateway is running"}
