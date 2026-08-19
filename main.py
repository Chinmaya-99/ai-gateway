from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.openapi.utils import get_openapi
from app.services.llm import router
from app.api.routes.health import router as health_router
from app.api.routes.chat import router as chat_router
from app.api.routes.embeddings import router as embeddings_router
from app.api.routes.cache import router as cache_router
from app.services.cache.cache_manager import CacheManager 
from app.api.routes.log_in import router as log_in_router
from app.api.routes.registration import router as registration_router
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
app.include_router(log_in_router, prefix="/auth/login")
app.include_router(registration_router, prefix="/auth/register")
@app.get("/")
async def root():
    return {"message": "AI Gateway is running"}


def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema

    openapi_schema = get_openapi(
        title=app.title,
        version="1.0.0",
        description="AI Gateway API",
        routes=app.routes,
    )

    openapi_schema["components"]["securitySchemes"] = {
        "BearerAuth": {
            "type": "http",
            "scheme": "bearer",
            "bearerFormat": "JWT",
        }
    }

    # Apply Bearer auth to every endpoint except public ones
    for path, methods in openapi_schema["paths"].items():
        if path.startswith("/auth/login") or path.startswith("/health") or path == "/":
            continue

        for operation in methods.values():
            operation["security"] = [{"BearerAuth": []}]

    app.openapi_schema = openapi_schema
    return app.openapi_schema


app.openapi = custom_openapi

