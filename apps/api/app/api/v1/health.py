from fastapi import APIRouter
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError

from app.db.database import engine

router = APIRouter(tags=["Health"])


@router.get("/")
def health_check():
    return {
        "status": "healthy",
        "service": "recall-api"
    }


@router.get("/db")
def database_health():
    try:
        with engine.connect() as connection:
            connection.execute(text("SELECT 1"))

        return {
            "status": "healthy",
            "database": "connected"
        }

    except SQLAlchemyError:
        return {
            "status": "unhealthy",
            "database": "connection failed"
        }