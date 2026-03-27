"""Pydantic schemas for quiz endpoints."""

from datetime import date, datetime
from pydantic import BaseModel


# â”€â”€ Sub-models â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€

class QuizOptionOut(BaseModel):
    id: str
    label: str
    option_text: str

    model_config = {"from_attributes": True}


class QuizOptionWithAnswer(QuizOptionOut):
    is_correct: bool


class QuizQuestionOut(BaseModel):
    id: str
    question_text: str
    order_index: int
    options: list[QuizOptionOut]

    model_config = {"from_attributes": True}


class QuizQuestionWithAnswer(BaseModel):
    id: str
    question_text: str
    explanation: str | None
    order_index: int
    options: list[QuizOptionWithAnswer]

    model_config = {"from_attributes": True}


# â”€â”€ Quiz â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€

class QuizOut(BaseModel):
    id: str
    quiz_date: date
    title: str
    questions: list[QuizQuestionOut]

    model_config = {"from_attributes": True}


# â”€â”€ Submit quiz â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€

class AnswerSubmit(BaseModel):
    question_id: str
    selected_option_id: str


class QuizSubmit(BaseModel):
    quiz_id: str
    answers: list[AnswerSubmit]


class QuizResultOut(BaseModel):
    score: int
    correct_count: int
    total_questions: int
    new_streak: int
    questions: list[QuizQuestionWithAnswer]  # with explanations


# â”€â”€ History & Leaderboard â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€

class QuizScoreOut(BaseModel):
    quiz_id: str
    quiz_date: date
    quiz_title: str
    score: int
    correct_count: int
    total_questions: int
    completed_at: datetime

    model_config = {"from_attributes": True}


class LeaderboardEntry(BaseModel):
    user_id: str
    full_name: str
    avatar_url: str | None
    total_score: int
    current_streak: int


# â”€â”€ Admin: Create Quiz â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€

class QuizOptionCreate(BaseModel):
    option_text: str
    is_correct: bool = False
    label: str  # A/B/C/D


class QuizQuestionCreate(BaseModel):
    question_text: str
    explanation: str | None = None
    order_index: int = 0
    options: list[QuizOptionCreate]


class QuizCreate(BaseModel):
    quiz_date: date
    title: str
    questions: list[QuizQuestionCreate]

