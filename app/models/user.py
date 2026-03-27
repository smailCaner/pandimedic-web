"""User ORM model."""

import uuid
from datetime import datetime, date
from sqlalchemy import String, Boolean, Integer, Date, DateTime, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database import Base


class User(Base):
    __tablename__ = "users"

    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=lambda: str(uuid.uuid4())
    )
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    password_hash: Mapped[str | None] = mapped_column(String(255), nullable=True)
    full_name: Mapped[str] = mapped_column(String(150))
    auth_provider: Mapped[str] = mapped_column(
        String(20), default="local"  # local / google / apple
    )
    auth_provider_id: Mapped[str | None] = mapped_column(String(255), nullable=True)
    avatar_url: Mapped[str | None] = mapped_column(String(500), nullable=True)

    # Gamification
    current_streak: Mapped[int] = mapped_column(Integer, default=0)
    longest_streak: Mapped[int] = mapped_column(Integer, default=0)
    total_score: Mapped[int] = mapped_column(Integer, default=0)
    last_quiz_date: Mapped[date | None] = mapped_column(Date, nullable=True)

    # Admin
    is_admin: Mapped[bool] = mapped_column(Boolean, default=False)

    # Timestamps
    created_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now(), onupdate=func.now()
    )

    # Relationships
    quiz_scores = relationship("QuizScore", back_populates="user", lazy="dynamic")
    symptom_logs = relationship("SymptomLog", back_populates="user", lazy="dynamic")

    def __repr__(self):
        return f"<User {self.email}>"
