"""Quiz API routes: daily quiz, submit, history, leaderboard."""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database import get_db
from app.core.deps import get_current_user
from app.models.user import User
from app.schemas.quiz import QuizOut, QuizSubmit, QuizResultOut, QuizScoreOut, LeaderboardEntry
from app.services import quiz_service

router = APIRouter(prefix="/api/quiz", tags=["Quiz"])


@router.get("/daily", response_model=QuizOut)
def daily_quiz(db: Session = Depends(get_db)):
    """Bugünkü günlük quiz'i getir (sorular + seçenekler, cevaplar gizli)."""
    return quiz_service.get_daily_quiz(db)


@router.post("/submit", response_model=QuizResultOut)
def submit_quiz(
    payload: QuizSubmit,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Quiz cevaplarını gönder. Skor, seri ve açıklamalar döner."""
    return quiz_service.submit_quiz(db, current_user, payload)


@router.get("/history", response_model=list[QuizScoreOut])
def quiz_history(
    limit: int = 30,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Kullanıcının quiz geçmişi (son N quiz)."""
    return quiz_service.get_quiz_history(db, current_user, limit)


@router.get("/leaderboard", response_model=list[LeaderboardEntry])
def leaderboard(limit: int = 20, db: Session = Depends(get_db)):
    """Skor tablosu — en yüksek toplam skora sahip kullanıcılar."""
    return quiz_service.get_leaderboard(db, limit)
