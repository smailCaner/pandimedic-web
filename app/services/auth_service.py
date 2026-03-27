"""Authentication service: register, login, profile."""

from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from app.models.user import User
from app.schemas.user import UserRegister, UserLogin, TokenResponse, UserProfile
from app.core.security import hash_password, verify_password, create_access_token


def register_user(db: Session, data: UserRegister) -> TokenResponse:
    """Register a new user with email/password."""
    existing = db.query(User).filter(User.email == data.email).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Bu e-posta adresi zaten kayıtlı",
        )
    user = User(
        email=data.email,
        password_hash=hash_password(data.password),
        full_name=data.full_name,
        auth_provider="local",
    )
    db.add(user)
    db.commit()
    db.refresh(user)

    token = create_access_token(data={"sub": str(user.id)})
    return TokenResponse(access_token=token)


def login_user(db: Session, data: UserLogin) -> TokenResponse:
    """Authenticate with email/password and return JWT."""
    user = db.query(User).filter(User.email == data.email).first()
    if not user or not user.password_hash:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Geçersiz e-posta veya şifre")
    if not verify_password(data.password, user.password_hash):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Geçersiz e-posta veya şifre")

    token = create_access_token(data={"sub": str(user.id)})
    return TokenResponse(access_token=token)


def get_profile(user: User) -> UserProfile:
    """Return user profile."""
    return UserProfile.model_validate(user)
