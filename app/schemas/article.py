"""Pydantic schemas for articles & medical library."""

from datetime import datetime
from pydantic import BaseModel


# â”€â”€ Requests â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€

class ArticleCreate(BaseModel):
    title: str
    content: str  # markdown
    category: str  # ilaÃ§ / hastalÄ±k / terim / genel
    slug: str
    is_published: bool = False
    tags: list[str] = []


class ArticleUpdate(BaseModel):
    title: str | None = None
    content: str | None = None
    category: str | None = None
    slug: str | None = None
    is_published: bool | None = None
    tags: list[str] | None = None


# â”€â”€ Responses â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€

class ArticleOut(BaseModel):
    id: str
    title: str
    content: str
    category: str
    slug: str
    is_published: bool
    tags: list[str] = []
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class ArticleListItem(BaseModel):
    id: str
    title: str
    category: str
    slug: str
    is_published: bool
    created_at: datetime

    model_config = {"from_attributes": True}

