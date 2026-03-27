"""Quiz ORM models: Quiz, QuizQuestion, QuizOption, QuizScore."""

import uuid
from datetime import datetime, date
from sqlalchemy import (
    String, Boolean, Integer, Date, DateTime, Text, ForeignKey,
    UniqueConstraint, func,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database import Base


class Quiz(Base):
    __tablename__ = "quizzes"

    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=lambda: str(uuid.uuid4())
    )
    quiz_date: Mapped[date] = mapped_column(Date, unique=True, index=True)
    title: Mapped[str] = mapped_column(String(300))
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now()
    )

    # Relationships
    questions = relationship(
        "QuizQuestion", back_populates="quiz", cascade="all, delete-orphan",
        order_by="QuizQuestion.order_index"
    )
    scores = relationship("QuizScore", back_populates="quiz", lazy="dynamic")

    def __repr__(self):
        return f"<Quiz {self.quiz_date}: {self.title}>"


class QuizQuestion(Base):
    __tablename__ = "quiz_questions"

    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=lambda: str(uuid.uuid4())
    )
    quiz_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("quizzes.id", ondelete="CASCADE")
    )
    question_text: Mapped[str] = mapped_column(Text)
    explanation: Mapped[str | None] = mapped_column(Text, nullable=True)
    order_index: Mapped[int] = mapped_column(Integer, default=0)

    # Relationships
    quiz = relationship("Quiz", back_populates="questions")
    options = relationship(
        "QuizOption", back_populates="question", cascade="all, delete-orphan",
        order_by="QuizOption.label"
    )

    def __repr__(self):
        return f"<QuizQuestion {self.order_index}: {self.question_text[:50]}>"


class QuizOption(Base):
    __tablename__ = "quiz_options"

    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=lambda: str(uuid.uuid4())
    )
    question_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("quiz_questions.id", ondelete="CASCADE")
    )
    option_text: Mapped[str] = mapped_column(String(500))
    is_correct: Mapped[bool] = mapped_column(Boolean, default=False)
    label: Mapped[str] = mapped_column(String(5))  # A, B, C, D

    # Relationships
    question = relationship("QuizQuestion", back_populates="options")

    def __repr__(self):
        return f"<QuizOption {self.label}: {self.option_text[:30]}>"


class QuizScore(Base):
    __tablename__ = "quiz_scores"
    __table_args__ = (
        UniqueConstraint("user_id", "quiz_id", name="uq_user_quiz"),
    )

    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=lambda: str(uuid.uuid4())
    )
    user_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("users.id", ondelete="CASCADE"), index=True
    )
    quiz_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("quizzes.id", ondelete="CASCADE"), index=True
    )
    score: Mapped[int] = mapped_column(Integer)
    correct_count: Mapped[int] = mapped_column(Integer)
    total_questions: Mapped[int] = mapped_column(Integer)
    completed_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now()
    )

    # Relationships
    user = relationship("User", back_populates="quiz_scores")
    quiz = relationship("Quiz", back_populates="scores")

    def __repr__(self):
        return f"<QuizScore user={self.user_id} score={self.score}>"
