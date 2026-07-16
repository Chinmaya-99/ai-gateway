from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.services.llm import router
from app.api.routes.health import router as health_router
from app.api.routes.chat import router as chat_router
from app.api.routes.embeddings import router as embeddings_router
from app.api.routes.cache import router as cache_router
from app.services.cache.cache_manager import CacheManager 
from app.api.routes.log_in import router as log_in_router
from app.middleware.logging_middleware import LoggingMiddleware
from app.middleware.auth_middleware import AuthMiddleware
from app.middleware.rate_limit_middleware import RateLimitMiddleware

from fastapi.security import OAuth2PasswordBearer

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")
@asynccontextmanager
async def lifespan(app: FastAPI):
    # ── Startup ────────────────────────────────────────────────────────
    app.state.cache_manager = await CacheManager.create()

    yield

    # ── Shutdown ───────────────────────────────────────────────────────
    await app.state.cache_manager.close()

app = FastAPI(title="AI Gateway", lifespan=lifespan)

# ── Middleware (order matters — bottom runs first) ─────────────────────────────
app.add_middleware(LoggingMiddleware)   # 3rd: logs after auth+rate checks
app.add_middleware(AuthMiddleware)      # 2nd: validates token + role
app.add_middleware(RateLimitMiddleware) # 1st: blocks brute force before anything
 

# ── Routers ─────────────────────────────────────────────────────────────────


app.include_router(health_router, prefix="/health")
app.include_router(chat_router, prefix="/chat")
app.include_router(embeddings_router, prefix="/embeddings")
app.include_router(cache_router, prefix="/cache")
app.include_router(log_in_router, prefix="/auth")

@app.get("/")
async def root():
    return {"message": "AI Gateway is running"}
