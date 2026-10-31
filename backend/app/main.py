import os
from contextlib import asynccontextmanager

from fastapi import APIRouter, FastAPI

from app.core.db import get_conn, init_schema
from app.routes.admin import router as admin_router
from app.routes.behaviors import router as behaviors_router
from app.routes.leads import router as leads_router


def _docs_enabled() -> bool:
    return os.getenv("ENABLE_DOCS", "true").strip().lower() in {"1", "true", "yes"}


@asynccontextmanager
async def lifespan(_app: FastAPI):
    init_schema()
    yield


_docs = _docs_enabled()
app = FastAPI(
    title="Deluxe Auto API",
    docs_url="/docs" if _docs else None,
    redoc_url="/redoc" if _docs else None,
    openapi_url="/openapi.json" if _docs else None,
    redirect_slashes=False,
    lifespan=lifespan,
)

api = APIRouter()
api.include_router(leads_router)
api.include_router(behaviors_router)
api.include_router(admin_router)


@api.get("/health")
def health() -> dict[str, str]:
    with get_conn() as conn, conn.cursor() as cur:
        cur.execute("SELECT 1")
    return {"status": "ok"}


app.include_router(api, prefix="/api")
