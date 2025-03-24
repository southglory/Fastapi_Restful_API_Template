"""
# File: fastapi_template/app/common/auth/jwt.py
# Description: JWT 인증 관련 유틸리티 함수
"""

from datetime import datetime, timedelta
from typing import Any, Dict, Optional, Union

import jwt
from pydantic import ValidationError

from app.common.config import dev_settings as settings
from app.common.exceptions import AuthenticationError
from app.db.schemas.token import TokenPayload


def create_access_token(
    subject: Union[str, Any], expires_delta: Optional[timedelta] = None
) -> str:
    """
    JWT 액세스 토큰 생성
    """
    if expires_delta:
        expire = datetime.now(datetime.UTC) + expires_delta
    else:
        expire = datetime.now(datetime.UTC) + timedelta(
            minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
        )

    to_encode = {"exp": expire, "sub": str(subject)}
    encoded_jwt = jwt.encode(
        to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM
    )
    return encoded_jwt


def verify_token(token: str) -> Dict[str, Any]:
    """
    JWT 토큰 검증 및 디코딩
    """
    try:
        payload = jwt.decode(
            token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM]
        )
        token_data = TokenPayload(**payload)

        if (
            token_data.exp is not None
            and datetime.fromtimestamp(float(token_data.exp)) < datetime.now(datetime.UTC)
        ):
            raise ValidationError("Token expired")

        return payload
    except jwt.PyJWTError:
        raise AuthenticationError("Could not validate credentials")
    except ValidationError:
        raise AuthenticationError("Token validation error")


def create_refresh_token(
    subject: Union[str, Any], expires_delta: Optional[timedelta] = None
) -> str:
    """
    JWT 리프레시 토큰 생성
    """
    if expires_delta:
        expire = datetime.now(datetime.UTC) + expires_delta
    else:
        expire = datetime.now(datetime.UTC) + timedelta(
            days=settings.REFRESH_TOKEN_EXPIRE_DAYS
        )

    to_encode = {"exp": expire, "sub": str(subject), "refresh": True}
    encoded_jwt = jwt.encode(
        to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM
    )
    return encoded_jwt
