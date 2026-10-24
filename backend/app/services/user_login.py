from fastapi import HTTPException, status
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models import User
from app.services.jwt_security import create_access_token
from app.services.password_security import verify_password


def login_user(db: Session, email: str, password: str) -> dict:
    normalized_email = email.strip().lower()

    user = db.scalar(
        select(User).where(func.lower(User.email) == normalized_email)
    )

    if (
        user is None
        or not user.is_active
        or not verify_password(password, user.hashed_password)
    ):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return {
        "access_token": create_access_token(user.id),
        "token_type": "bearer",
    }
