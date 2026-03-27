"""Quiz service: daily quiz, submission, scoring, streak management."""

from datetime import date, timedelta
from sqlalchemy.orm import Session, joinedload
from fastapi import HTTPException, status
from app.models.quiz import Quiz, QuizQuestion, QuizOption, QuizScore
from app.models.user import User
from app.schemas.quiz import (
    QuizOut, QuizSubmit, QuizResultOut, QuizScoreOut,
    LeaderboardEntry, QuizQuestionWithAnswer, QuizOptionWithAnswer,
)


def get_daily_quiz(db: Session, target_date: date | None = None) -> QuizOut:
    """Return today's quiz with questions and options (without correct answers)."""
    quiz_date = target_date or date.today()
    quiz = (
        db.query(Quiz)
        .options(joinedload(Quiz.questions).joinedload(QuizQuestion.options))
        .filter(Quiz.quiz_date == quiz_date, Quiz.is_active == True)
        .first()
    )
    if not quiz:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Bugün için quiz bulunamadı",
        )
    return QuizOut.model_validate(quiz)


def submit_quiz(db: Session, user: User, payload: QuizSubmit) -> QuizResultOut:
    """Grade quiz answers, update streak, and return results with explanations."""
    # Check if already submitted
    existing = (
        db.query(QuizScore)
        .filter(QuizScore.user_id == user.id, QuizScore.quiz_id == payload.quiz_id)
        .first()
    )
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Bu quiz'i zaten çözdünüz",
        )

    # Load quiz with answers
    quiz = (
        db.query(Quiz)
        .options(joinedload(Quiz.questions).joinedload(QuizQuestion.options))
        .filter(Quiz.id == payload.quiz_id)
        .first()
    )
    if not quiz:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Quiz bulunamadı")

    # Build answer lookup: question_id -> selected_option_id
    answer_map = {str(a.question_id): str(a.selected_option_id) for a in payload.answers}

    # Grade
    correct_count = 0
    total = len(quiz.questions)
    for question in quiz.questions:
        correct_option = next((o for o in question.options if o.is_correct), None)
        selected = answer_map.get(str(question.id))
        if correct_option and selected == str(correct_option.id):
            correct_count += 1

    score = int((correct_count / total) * 100) if total > 0 else 0

    # Save score
    quiz_score = QuizScore(
        user_id=user.id,
        quiz_id=payload.quiz_id,
        score=score,
        correct_count=correct_count,
        total_questions=total,
    )
    db.add(quiz_score)

    # Update streak
    today = date.today()
    if user.last_quiz_date is None or user.last_quiz_date < today - timedelta(days=1):
        user.current_streak = 1
    elif user.last_quiz_date == today - timedelta(days=1):
        user.current_streak += 1
    # If same day, streak stays the same

    user.last_quiz_date = today
    user.longest_streak = max(user.longest_streak, user.current_streak)
    user.total_score += score

    db.commit()
    db.refresh(user)

    # Build result with explanations
    questions_with_answers = [
        QuizQuestionWithAnswer(
            id=q.id,
            question_text=q.question_text,
            explanation=q.explanation,
            order_index=q.order_index,
            options=[
                QuizOptionWithAnswer(
                    id=o.id,
                    label=o.label,
                    option_text=o.option_text,
                    is_correct=o.is_correct,
                )
                for o in q.options
            ],
        )
        for q in quiz.questions
    ]

    return QuizResultOut(
        score=score,
        correct_count=correct_count,
        total_questions=total,
        new_streak=user.current_streak,
        questions=questions_with_answers,
    )


def get_quiz_history(db: Session, user: User, limit: int = 30) -> list[QuizScoreOut]:
    """Return user's recent quiz scores."""
    scores = (
        db.query(QuizScore)
        .join(Quiz)
        .filter(QuizScore.user_id == user.id)
        .order_by(QuizScore.completed_at.desc())
        .limit(limit)
        .all()
    )
    return [
        QuizScoreOut(
            quiz_id=s.quiz_id,
            quiz_date=s.quiz.quiz_date,
            quiz_title=s.quiz.title,
            score=s.score,
            correct_count=s.correct_count,
            total_questions=s.total_questions,
            completed_at=s.completed_at,
        )
        for s in scores
    ]


def get_leaderboard(db: Session, limit: int = 20) -> list[LeaderboardEntry]:
    """Top users by total score."""
    users = (
        db.query(User)
        .order_by(User.total_score.desc())
        .limit(limit)
        .all()
    )
    return [
        LeaderboardEntry(
            user_id=u.id,
            full_name=u.full_name,
            avatar_url=u.avatar_url,
            total_score=u.total_score,
            current_streak=u.current_streak,
        )
        for u in users
    ]
