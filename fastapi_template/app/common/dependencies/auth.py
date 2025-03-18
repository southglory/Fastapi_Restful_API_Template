"""
# File: fastapi_template/app/common/dependencies/auth.py
# Description: 인증 및 권한 관련 의존성 함수
# - 토큰 검증
# - 사용자 인증
# - 권한 확인
"""

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError
from sqlalchemy.ext.asyncio import AsyncSession

from app.common.auth import verify_token
from app.common.config import settings
from app.common.database import get_db
from app.common.exceptions import AuthenticationError
from app.services.user_service import UserService

oauth2_scheme = OAuth2PasswordBearer(tokenUrl=f"{settings.API_V1_STR}/auth/login")


async def get_current_user(
    token: str = Depends(oauth2_scheme), db: AsyncSession = Depends(get_db)
):
    """현재 인증된 사용자 정보를 가져오는 의존성 함수"""
    try:
        payload = verify_token(token)
        user_id = payload.get("sub")
        if not user_id:
            raise AuthenticationError("Invalid token")
    except JWTError:
        raise AuthenticationError("Invalid token")

    user = await UserService.get_user(db, user_id=user_id)
    if not user:
        raise AuthenticationError("User not found")

    return user


async def get_current_active_user(current_user=Depends(get_current_user)):
    """활성화된 사용자인지 확인하는 의존성 함수"""
    if not current_user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Inactive user"
        )
    return current_user


async def get_current_admin_user(current_user=Depends(get_current_user)):
    """관리자 권한을 가진 사용자인지 확인하는 의존성 함수"""
    if not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Not enough privileges"
        )
    return current_user
