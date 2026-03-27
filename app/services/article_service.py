"""Article service: CRUD operations for the medical library."""

from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from app.models.article import Article, ArticleTag
from app.models.user import User
from app.schemas.article import ArticleCreate, ArticleUpdate, ArticleOut, ArticleListItem


def list_articles(
    db: Session,
    search: str | None = None,
    category: str | None = None,
    published_only: bool = True,
    skip: int = 0,
    limit: int = 20,
) -> list[ArticleListItem]:
    """List articles with optional search and category filter."""
    query = db.query(Article)

    if published_only:
        query = query.filter(Article.is_published == True)
    if category:
        query = query.filter(Article.category == category)
    if search:
        query = query.filter(
            Article.title.ilike(f"%{search}%") | Article.content.ilike(f"%{search}%")
        )

    articles = query.order_by(Article.created_at.desc()).offset(skip).limit(limit).all()
    return [ArticleListItem.model_validate(a) for a in articles]


def get_article_by_slug(db: Session, slug: str) -> ArticleOut:
    """Get a single article by slug."""
    article = db.query(Article).filter(Article.slug == slug).first()
    if not article:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Makale bulunamadı")

    return ArticleOut(
        id=article.id,
        title=article.title,
        content=article.content,
        category=article.category,
        slug=article.slug,
        is_published=article.is_published,
        tags=[t.tag for t in article.tags],
        created_at=article.created_at,
        updated_at=article.updated_at,
    )


def create_article(db: Session, data: ArticleCreate, admin: User) -> ArticleOut:
    """Create a new article (admin only)."""
    existing = db.query(Article).filter(Article.slug == data.slug).first()
    if existing:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Bu slug zaten kullanılıyor")

    article = Article(
        title=data.title,
        content=data.content,
        category=data.category,
        slug=data.slug,
        is_published=data.is_published,
        created_by=admin.id,
    )
    db.add(article)
    db.flush()

    for tag_name in data.tags:
        db.add(ArticleTag(article_id=article.id, tag=tag_name))

    db.commit()
    db.refresh(article)
    return get_article_by_slug(db, article.slug)


def update_article(db: Session, article_id: str, data: ArticleUpdate) -> ArticleOut:
    """Update an existing article (admin only)."""
    article = db.query(Article).filter(Article.id == article_id).first()
    if not article:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Makale bulunamadı")

    if data.title is not None:
        article.title = data.title
    if data.content is not None:
        article.content = data.content
    if data.category is not None:
        article.category = data.category
    if data.slug is not None:
        article.slug = data.slug
    if data.is_published is not None:
        article.is_published = data.is_published
    if data.tags is not None:
        # Replace all tags
        db.query(ArticleTag).filter(ArticleTag.article_id == article.id).delete()
        for tag_name in data.tags:
            db.add(ArticleTag(article_id=article.id, tag=tag_name))

    db.commit()
    db.refresh(article)
    return get_article_by_slug(db, article.slug)


def delete_article(db: Session, article_id: str) -> dict:
    """Delete an article (admin only)."""
    article = db.query(Article).filter(Article.id == article_id).first()
    if not article:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Makale bulunamadı")

    db.delete(article)
    db.commit()
    return {"detail": "Makale silindi"}
