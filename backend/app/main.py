"""
COSIB backend entrypoint.

Run locally with:
    uvicorn app.main:app --reload

Run in production (Railway):
    uvicorn app.main:app --host 0.0.0.0 --port $PORT
(see backend/Dockerfile — Railway injects PORT automatically)
"""
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware

from app.api.v1.router import api_router
from app.core.config import settings
from app.core.exceptions import register_exception_handlers
from app.core.limiter import limiter
from app.core.logging import configure_logging, logger


@asynccontextmanager
async def lifespan(app: FastAPI):
    configure_logging()
    logger.info("cosib.startup", environment=settings.APP_ENV)
    yield
    logger.info("cosib.shutdown")


app = FastAPI(
    title=f"{settings.APP_NAME} API",
    description="AI-Powered Academic Virtual Assistant for the Computer Science "
    f"Department of {settings.INSTITUTION_NAME}",
    version="1.0.0",
    docs_url="/api/docs",
    redoc_url="/api/redoc",
    openapi_url="/api/openapi.json",
    lifespan=lifespan,
)

# --- CORS ---
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_origin_regex=settings.CORS_ORIGIN_REGEX or None,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Security headers ---
@app.middleware("http")
async def add_security_headers(request, call_next):
    response = await call_next(request)
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
    response.headers["Permissions-Policy"] = "geolocation=(), microphone=(), camera=()"
    if settings.APP_ENV == "production":
        response.headers["Strict-Transport-Security"] = "max-age=63072000; includeSubDomains"
    return response


# --- Rate limiting ---
app.state.limiter = limiter
app.add_middleware(SlowAPIMiddleware)


@app.exception_handler(RateLimitExceeded)
async def rate_limit_handler(request, exc):
    from fastapi.responses import JSONResponse

    return JSONResponse(
        status_code=429,
        content={"success": False, "error": {"code": "RATE_LIMITED", "message": "Too many requests"}},
    )


# --- Global exception handlers ---
register_exception_handlers(app)

# --- Routes ---
app.include_router(api_router, prefix=settings.API_V1_PREFIX)


@app.get("/")
async def root():
    return {
        "app": settings.APP_NAME,
        "message": "Your Intelligent Academic Companion",
        "docs": "/api/docs",
    }
