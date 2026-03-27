"""Auth API routes: register, login, profile."""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database import get_db
from app.core.deps import get_current_user
from app.models.user import User
from app.schemas.user import UserRegister, UserLogin, TokenResponse, UserProfile
from app.services import auth_service

router = APIRouter(prefix="/api/auth", tags=["Auth"])


@router.post("/register", response_model=TokenResponse)
def register(data: UserRegister, db: Session = Depends(get_db)):
    """Yeni kullanıcı kaydı (e-posta + şifre)."""
    return auth_service.register_user(db, data)


@router.post("/login", response_model=TokenResponse)
def login(data: UserLogin, db: Session = Depends(get_db)):
    """E-posta ile giriş. JWT token döner."""
    return auth_service.login_user(db, data)


@router.get("/me", response_model=UserProfile)
def me(current_user: User = Depends(get_current_user)):
    """Mevcut kullanıcı profili (streak, skor, vb.)."""
    return auth_service.get_profile(current_user)
