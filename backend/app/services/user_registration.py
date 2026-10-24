from fastapi import HTTPException
from sqlalchemy import func, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.models import User
from app.schemas.user import UserRegister
from app.services.password_security import hash_password


def register_user(db: Session, payload: UserRegister) -> User:
    email = str(payload.email).strip().lower()

    existing = db.scalar(
        select(User).where(func.lower(User.email) == email)
    )

    if existing is not None:
        raise HTTPException(
            status_code=409,
            detail="An account with this email already exists.",
        )

    user = User(
        full_name=payload.full_name,
        email=email,
        hashed_password=hash_password(payload.password),
        is_active=True,
    )

    db.add(user)

    try:
        db.commit()
        db.refresh(user)
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=409,
            detail="An account with this email already exists.",
        )

    return user
