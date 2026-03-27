"""Pandimedic FastAPI Application — Entry Point."""

import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from app.config import get_settings
from app.database import engine, Base

# Import all models so SQLAlchemy knows about them
from app.models import user, quiz, article, symptom  # noqa: F401

# Import routers
from app.api.auth import router as auth_router
from app.api.quiz import router as quiz_router
from app.api.articles import router as articles_router
from app.api.symptoms import router as symptoms_router
from app.api.admin import router as admin_router
from app.seed import seed as run_seed

settings = get_settings()

# Create all tables
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title=settings.APP_NAME,
    description=(
        "Tıbbi okuryazarlığı artırmak için oyunlaştırma içeren mobil uygulama API'si. "
        "Günlük quiz, tıbbi kütüphane, semptom analizi ve E-Nabız yönlendirmesi."
    ),
    version="0.1.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

# CORS — Flutter & React admin panel için tüm originlere izin ver (development)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Production'da kısıtlanmalı
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register routers
app.include_router(auth_router)
app.include_router(quiz_router)
app.include_router(articles_router)
app.include_router(symptoms_router)
app.include_router(admin_router)

# Serve static files (frontend)
STATIC_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "static")
if os.path.isdir(STATIC_DIR):
    app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")


@app.get("/", tags=["Root"])
def root():
    """Serve the frontend HTML page."""
    index_path = os.path.join(STATIC_DIR, "index.html")
    if os.path.exists(index_path):
        return FileResponse(index_path, media_type="text/html")
    return {
        "app": settings.APP_NAME,
        "version": "0.1.0",
        "docs": "/docs",
        "status": "running ✅",
    }


@app.on_event("startup")
def startup_seed():
    """Auto-seed database on startup if empty."""
    try:
        from app.database import SessionLocal
        from app.models.quiz import Quiz
        db = SessionLocal()
        if db.query(Quiz).count() == 0:
            db.close()
            run_seed()
        else:
            db.close()
    except Exception as e:
        print(f"Auto-seed skipped: {e}")


@app.get("/health", tags=["Root"])
def health_check():
    return {"status": "healthy"}
