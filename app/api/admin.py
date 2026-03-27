"""Admin API routes: article CRUD, quiz creation, users, stats."""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.database import get_db
from app.core.deps import get_admin_user
from app.models.user import User
from app.models.quiz import Quiz, QuizQuestion, QuizOption, QuizScore
from app.models.article import Article
from app.schemas.article import ArticleCreate, ArticleUpdate, ArticleOut, ArticleListItem
from app.schemas.quiz import QuizCreate, QuizOut
from app.schemas.user import UserProfile
from app.services import article_service

router = APIRouter(prefix="/api/admin", tags=["Admin"])


# ── Article Management ────────────────────────────────────────────────────────

@router.get("/articles", response_model=list[ArticleListItem])
def admin_list_articles(
    skip: int = 0,
    limit: int = 50,
    db: Session = Depends(get_db),
    admin: User = Depends(get_admin_user),
):
    """Tüm makaleleri listele (yayımlanmamış dahil)."""
    return article_service.list_articles(db, published_only=False, skip=skip, limit=limit)


@router.post("/articles", response_model=ArticleOut)
def admin_create_article(
    data: ArticleCreate,
    db: Session = Depends(get_db),
    admin: User = Depends(get_admin_user),
):
    """Yeni makale oluştur."""
    return article_service.create_article(db, data, admin)


@router.put("/articles/{article_id}", response_model=ArticleOut)
def admin_update_article(
    article_id: str,
    data: ArticleUpdate,
    db: Session = Depends(get_db),
    admin: User = Depends(get_admin_user),
):
    """Makale güncelle."""
    return article_service.update_article(db, article_id, data)


@router.delete("/articles/{article_id}")
def admin_delete_article(
    article_id: str,
    db: Session = Depends(get_db),
    admin: User = Depends(get_admin_user),
):
    """Makale sil."""
    return article_service.delete_article(db, article_id)


# ── Quiz Management ──────────────────────────────────────────────────────────

@router.post("/quiz", response_model=QuizOut)
def admin_create_quiz(
    data: QuizCreate,
    db: Session = Depends(get_db),
    admin: User = Depends(get_admin_user),
):
    """Yeni günlük quiz oluştur (sorular ve seçeneklerle birlikte)."""
    quiz = Quiz(
        quiz_date=data.quiz_date,
        title=data.title,
    )
    db.add(quiz)
    db.flush()

    for q_data in data.questions:
        question = QuizQuestion(
            quiz_id=quiz.id,
            question_text=q_data.question_text,
            explanation=q_data.explanation,
            order_index=q_data.order_index,
        )
        db.add(question)
        db.flush()

        for opt in q_data.options:
            option = QuizOption(
                question_id=question.id,
                option_text=opt.option_text,
                is_correct=opt.is_correct,
                label=opt.label,
            )
            db.add(option)

    db.commit()
    db.refresh(quiz)

    return QuizOut.model_validate(quiz)


# ── User Management ──────────────────────────────────────────────────────────

@router.get("/users", response_model=list[UserProfile])
def admin_list_users(
    skip: int = 0,
    limit: int = 50,
    db: Session = Depends(get_db),
    admin: User = Depends(get_admin_user),
):
    """Tüm kullanıcıları listele."""
    users = db.query(User).order_by(User.created_at.desc()).offset(skip).limit(limit).all()
    return [UserProfile.model_validate(u) for u in users]


# ── Dashboard Stats ──────────────────────────────────────────────────────────

@router.get("/stats")
def admin_stats(
    db: Session = Depends(get_db),
    admin: User = Depends(get_admin_user),
):
    """Dashboard istatistikleri."""
    total_users = db.query(func.count(User.id)).scalar()
    total_quizzes = db.query(func.count(Quiz.id)).scalar()
    total_articles = db.query(func.count(Article.id)).scalar()
    total_quiz_submissions = db.query(func.count(QuizScore.id)).scalar()
    published_articles = db.query(func.count(Article.id)).filter(Article.is_published == True).scalar()

    return {
        "total_users": total_users,
        "total_quizzes": total_quizzes,
        "total_articles": total_articles,
        "published_articles": published_articles,
        "total_quiz_submissions": total_quiz_submissions,
    }
