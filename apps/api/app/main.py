
from fastapi import FastAPI
from sqlalchemy import create_engine, text
from sqlalchemy.exc import SQLAlchemyError
import os

app = FastAPI(
    title="RECALL API",
    description="Learning Intelligence Platform",
    version="0.1.0"
)

DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql+psycopg2://recall_user:recall_dev_password@localhost:5432/recall_db"
)

engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True
)


@app.get("/")
def root():
    return {
        "name": "RECALL",
        "message": "Learning Intelligence API is running",
        "version": "0.1.0"
    }


@app.get("/health")
def health():
    return {
        "status": "healthy",
        "service": "recall-api"
    }


@app.get("/health/db")
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
