
from fastapi import FastAPI

from app.core.config import settings
from app.api.v1.health import router as health_router
from app.api.v1.routes.users import router as users_router
from app.api.v1.routes.subjects import router as subjects_router
from app.api.v1.routes.materials import router as materials_router

app = FastAPI(
    title="RECALL API",
    description="AI-powered Learning Intelligence Platform",
    version="0.1.0"
)


@app.get("/")
def root():
    return {
        "name": settings.APP_NAME,
        "message": "Learning Intelligence API is running",
        "version": "0.1.0"
    }


app.include_router(health_router, prefix="/health")
app.include_router(users_router, prefix="/api/v1")
app.include_router(subjects_router, prefix="/api/v1")
app.include_router(
    materials_router,
    prefix="/api/v1"
)
