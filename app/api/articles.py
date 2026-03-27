"""Articles API routes: public listing and detail."""

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from app.database import get_db
from app.schemas.article import ArticleOut, ArticleListItem
from app.services import article_service

router = APIRouter(prefix="/api/articles", tags=["Articles"])


@router.get("", response_model=list[ArticleListItem])
def list_articles(
    search: str | None = Query(None, description="Arama terimi"),
    category: str | None = Query(None, description="Kategori filtresi (ilaç/hastalık/terim/genel)"),
    skip: int = 0,
    limit: int = 20,
    db: Session = Depends(get_db),
):
    """Yayımlanmış makaleleri listele (arama + kategori filtresi)."""
    return article_service.list_articles(db, search=search, category=category, skip=skip, limit=limit)


@router.get("/{slug}", response_model=ArticleOut)
def get_article(slug: str, db: Session = Depends(get_db)):
    """Slug ile tek makale detayı."""
    return article_service.get_article_by_slug(db, slug)
