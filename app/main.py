from fastapi import FastAPI

from app.api.routes.health import router as health_router
from app.api.routes.macro import router as macro_router
from app.core.config import settings

app = FastAPI(
    title=settings.app_name,
    version="0.1.0",
    description="Independent AI assistant for portfolio research and market/macro analysis.",
)

app.include_router(health_router, prefix=settings.api_prefix)
app.include_router(macro_router, prefix=settings.api_prefix)


@app.get("/", tags=["root"])
async def root() -> dict[str, str]:
    return {"name": settings.app_name, "status": "running"}
