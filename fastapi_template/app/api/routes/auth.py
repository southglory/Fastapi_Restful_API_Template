"""
# File: fastapi_template/app/api/routes/auth.py
# Description: 인증 관련 API 엔드포인트 정의
# - JWT 토큰 발급 및 갱신
# - 로그인/로그아웃 처리
# - 인증 상태 확인
"""

from datetime import timedelta
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession

from app.common.auth import create_access_token
from fastapi_template.app.common.config import config_settings
from app.common.exceptions import AuthenticationError
from app.common.database import get_db
from app.db.schemas.token import Token
from app.services.user_service import UserService

router = APIRouter()


@router.post("/login", response_model=Token)
async def login_for_access_token(
    form_data: OAuth2PasswordRequestForm = Depends(), db: AsyncSession = Depends(get_db)
) -> Any:
    """
    OAuth2 호환 토큰 로그인, JWT 액세스 토큰 반환
    """
    user = await UserService.authenticate_user(
        db, form_data.username, form_data.password
    )
    if not user:
        raise AuthenticationError("Incorrect email or password")

    access_token_expires = timedelta(minutes=config_settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        subject=user.id, expires_delta=access_token_expires
    )

    return {"access_token": access_token, "token_type": "bearer"}
