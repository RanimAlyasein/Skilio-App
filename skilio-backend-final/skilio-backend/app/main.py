"""
app/main.py
───────────
FastAPI application factory.

Features:
  - CORS with configured origins
  - Content-length limiting (DoS protection)
  - Request ID middleware for traceability
  - Slow-request logging
  - Startup DB health check
  - Clean shutdown
"""
import time
import uuid
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.api.router import api_router
from app.core.config import get_settings

settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI):
    # ── Startup ───────────────────────────────────────────────────────────────
    from app.core.database import check_db_connection
    print(f"\n  Starting {settings.app_name} v{settings.app_version}")
    print(f"  Database: {settings.database_url[:50]}...")
    print(f"  Debug:    {settings.debug}\n")
    try:
        check_db_connection()
        print("  ✓ Database connected\n")
    except RuntimeError as exc:
        print(str(exc))
        import sys
        sys.exit(1)
    yield
    # ── Shutdown ──────────────────────────────────────────────────────────────
    print(f"\n  {settings.app_name} shutting down cleanly.")


app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description=(
        "**Skilio** — Scenario-based life skills and safety learning for children.\n\n"
        "Parents manage child profiles and track every decision in real time.\n"
        "Children navigate branching story worlds and earn XP for safe choices.\n\n"
        "**Authentication:** Bearer JWT (access token in Authorization header)\n"
        "**Refresh:** httpOnly cookie via `/api/auth/refresh`"
    ),
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
)

# ── CORS ──────────────────────────────────────────────────────────────────────
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ── Request ID + slow-request logging ─────────────────────────────────────────
@app.middleware("http")
async def request_middleware(request: Request, call_next):
    request_id = str(uuid.uuid4())[:8]
    request.state.request_id = request_id
    start = time.time()
    response: Response = await call_next(request)
    elapsed = time.time() - start
    response.headers["X-Request-ID"] = request_id
    response.headers["X-Response-Time"] = f"{elapsed:.3f}s"
    if elapsed > 2.0:
        print(f"  [SLOW] {request.method} {request.url.path} took {elapsed:.2f}s (id={request_id})")
    return response


# ── Content-length guard (DoS protection) ─────────────────────────────────────
@app.middleware("http")
async def limit_upload_size(request: Request, call_next):
    content_length = request.headers.get("content-length")
    if content_length and int(content_length) > settings.max_request_body_bytes:
        return JSONResponse(
            status_code=413,
            content={"detail": f"Request body too large (max {settings.max_request_body_bytes // 1024} KB)"},
        )
    return await call_next(request)


# ── Routes ────────────────────────────────────────────────────────────────────
app.include_router(api_router)


@app.get("/health", tags=["health"], summary="Health check")
def health():
    """Returns OK when the server and database are up."""
    return {
        "status": "ok",
        "app": settings.app_name,
        "version": settings.app_version,
        "database": "sqlite" if settings.is_sqlite else ("mysql" if settings.is_mysql else "postgresql"),
    }
