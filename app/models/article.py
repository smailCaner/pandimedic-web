"""Article ORM models: Article, ArticleTag."""

import uuid
from datetime import datetime
from sqlalchemy import String, Boolean, Text, DateTime, ForeignKey, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database import Base


class Article(Base):
    __tablename__ = "articles"

    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=lambda: str(uuid.uuid4())
    )
    title: Mapped[str] = mapped_column(String(500))
    content: Mapped[str] = mapped_column(Text)  # Markdown content
    category: Mapped[str] = mapped_column(
        String(50), index=True  # ilaç / hastalık / terim / genel
    )
    slug: Mapped[str] = mapped_column(String(500), unique=True, index=True)
    is_published: Mapped[bool] = mapped_column(Boolean, default=False)
    created_by: Mapped[str | None] = mapped_column(
        String(36), ForeignKey("users.id"), nullable=True
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now(), onupdate=func.now()
    )

    # Relationships
    tags = relationship(
        "ArticleTag", back_populates="article", cascade="all, delete-orphan"
    )
    author = relationship("User", foreign_keys=[created_by])

    def __repr__(self):
        return f"<Article {self.slug}>"


class ArticleTag(Base):
    __tablename__ = "article_tags"

    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=lambda: str(uuid.uuid4())
    )
    article_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("articles.id", ondelete="CASCADE"), index=True
    )
    tag: Mapped[str] = mapped_column(String(100), index=True)

    # Relationships
    article = relationship("Article", back_populates="tags")

    def __repr__(self):
        return f"<ArticleTag {self.tag}>"
