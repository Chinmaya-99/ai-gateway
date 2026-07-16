from fastapi import Request
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
from app.services.auth.auth_service import AuthService, AuthError
from app.models.token_model import TokenData

auth_service = AuthService()

# ── Route Rules ───────────────────────────────────────────────────────────────

PUBLIC_ROUTES = [
    "/auth/login",
    "/health",
    "/",    
    "/favicon.ico",  
    "/docs",
    "/openapi.json"
]

ADMIN_ONLY_ROUTES = [
    "/auth/register",
    "/cache",
]

USER_ROUTES = [
    "/chat",
    "/embeddings",
]


def get_route_role(path: str) -> str | None:
    """
    Returns the required role for a path:
      - None     → public, no token needed
      - "admin"  → admin only
      - "user"   → user or admin
    """
    for route in PUBLIC_ROUTES:
        if path == route or path.startswith(route + "/"):
            return None

    for route in ADMIN_ONLY_ROUTES:
        if path == route or path.startswith(route + "/"):
            return "admin"

    for route in USER_ROUTES:
        if path == route or path.startswith(route + "/"):
            return "user"

    # Default: require at least a valid token for unknown routes
    return "user"


# ── Middleware ─────────────────────────────────────────────────────────────────

class AuthMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        path = request.url.path
        required_role = get_route_role(path)

        # Public route — skip auth entirely
        if required_role is None:
            return await call_next(request)

        # Extract token from Authorization header
        auth_header = request.headers.get("Authorization")
        if not auth_header or not auth_header.startswith("Bearer "):
            return JSONResponse(
                status_code=401,
                content={"detail": "Missing or invalid Authorization header."}
            )

        token = auth_header.split(" ", 1)[1]

        # Decode and validate token
        try:
            token_data: TokenData = auth_service.decode_token(token)
        except AuthError as e:
            return JSONResponse(
                status_code=401,
                content={"detail": str(e.error)}
            )

        # Role check
        if required_role == "admin" and token_data.role != "admin":
            return JSONResponse(
                status_code=403,
                content={"detail": "Admin privileges required."}
            )

        # Attach user to request state for use in route handlers
        request.state.user = token_data

        return await call_next(request)