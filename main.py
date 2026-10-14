from contextlib import asynccontextmanager
from fastapi import FastAPI

from app.config import settings
from app.database import init_db
from app.routes.base import api_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    yield


app = FastAPI(
    title=settings.app_name,
    description="Student CRUD API built as an EWB Python backend internship project.",
    version="1.0.0",
    lifespan=lifespan,
)
app.include_router(api_router)


@app.get("/", tags=["System"])
def root():
    return {"message": "Student Management API is running", "docs": "/docs", "health": "/health"}


@app.get("/health", tags=["System"])
def health():
    return {"status": "ok"}
