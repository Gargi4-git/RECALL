from fastapi import FastAPI

from app.core.config import settings
from app.api.v1.health import router as health_router


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


app.include_router(
    health_router,
    prefix="/health"
)