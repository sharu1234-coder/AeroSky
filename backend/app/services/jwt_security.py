import os
from datetime import datetime, timedelta, timezone

import jwt
from fastapi import HTTPException, status
from jwt.exceptions import InvalidTokenError


ALGORITHM = "HS256"
ACCESS_TOKEN_MINUTES = 60


def get_jwt_secret() -> str:
    secret = os.getenv("JWT_SECRET_KEY")

    if not secret:
        from dotenv import load_dotenv
        load_dotenv()
        secret = os.getenv("JWT_SECRET_KEY")

    if not secret or len(secret) < 32:
        raise RuntimeError("JWT_SECRET_KEY must contain at least 32 characters.")

    return secret


def create_access_token(user_id: int) -> str:
    now = datetime.now(timezone.utc)

    payload = {
        "sub": str(user_id),
        "iat": now,
        "nbf": now,
        "exp": now + timedelta(minutes=ACCESS_TOKEN_MINUTES),
        "type": "access",
    }

    return jwt.encode(
        payload,
        get_jwt_secret(),
        algorithm=ALGORITHM,
    )


def decode_access_token(token: str) -> int:
    credentials_error = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid or expired access token.",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        payload = jwt.decode(
            token,
            get_jwt_secret(),
            algorithms=[ALGORITHM],
            options={"require": ["sub", "iat", "nbf", "exp"]},
        )

        if payload.get("type") != "access":
            raise credentials_error

        subject = payload.get("sub")

        if not isinstance(subject, str) or not subject.isdecimal():
            raise credentials_error

        user_id = int(subject)

        if user_id <= 0:
            raise credentials_error

        return user_id

    except InvalidTokenError:
        raise credentials_error
