"""
app/api/router.py
─────────────────
Central router aggregator — the only file main.py needs to know about.

All domain routers are imported and registered here with their URL prefixes
and OpenAPI tags. Adding a new domain means one line in this file.
"""

from fastapi import APIRouter

from app.api.auth      import router as auth_router
from app.api.users     import router as users_router
from app.api.children  import router as children_router
from app.api.modules   import router as modules_router
from app.api.lessons   import router as lessons_router
from app.api.scenarios import router as scenarios_router
from app.api.badges    import router as badges_router

api_router = APIRouter(prefix="/api")

api_router.include_router(auth_router,      prefix="/auth",      tags=["auth"])
api_router.include_router(users_router,     prefix="/users",     tags=["users"])
api_router.include_router(children_router,  prefix="/children",  tags=["children"])
api_router.include_router(modules_router,   prefix="/modules",   tags=["modules"])
api_router.include_router(lessons_router,   prefix="/lessons",   tags=["lessons"])
api_router.include_router(scenarios_router, prefix="/scenarios", tags=["scenarios"])
api_router.include_router(badges_router,    prefix="/badges",    tags=["badges"])
