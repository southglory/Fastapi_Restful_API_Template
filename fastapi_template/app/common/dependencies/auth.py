"""
# File: fastapi_template/app/common/dependencies/auth.py
# Description: 인증 및 권한 관련 의존성 함수
# - 토큰 검증
# - 사용자 인증
# - 권한 확인
"""

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
import jwt
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional

from app.common.auth import verify_token
from fastapi_template.app.common.config import config_settings
from app.common.database import get_db
from app.common.exceptions import AuthenticationError
from app.services.user_service import UserService

oauth2_scheme = OAuth2PasswordBearer(tokenUrl=f"{config_settings.API_V1_STR}/auth/login")


async def get_current_user(
    token: str = Depends(oauth2_scheme), db: AsyncSession = Depends(get_db)
):
    """현재 인증된 사용자 정보를 가져오는 의존성 함수"""
    try:
        payload = verify_token(token)
        user_id = payload.get("sub")
        if not user_id:
            raise AuthenticationError("Invalid token")
    except jwt.PyJWTError:
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


def has_permission(required_role: str):
    """
    사용자가 특정 역할이나 권한을 가지고 있는지 확인하는 의존성 함수
    
    사용 예시:
    @app.get("/admin")
    async def admin_route(user = Depends(has_permission("admin"))):
        return {"message": "You have admin access"}
    """
    
    async def permission_dependency(current_user=Depends(get_current_user)):
        if not hasattr(current_user, "role") or current_user.role != required_role:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Permission denied"
            )
        return current_user
    
    return permission_dependency


def has_any_permission(required_roles: List[str]):
    """
    사용자가 주어진 역할 목록 중 하나라도 가지고 있는지 확인하는 의존성 함수
    
    사용 예시:
    @app.get("/restricted")
    async def restricted_route(user = Depends(has_any_permission(["admin", "moderator"]))):
        return {"message": "You have access to restricted area"}
    """
    
    async def permission_dependency(current_user=Depends(get_current_user)):
        if not hasattr(current_user, "role") or current_user.role not in required_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Permission denied"
            )
        return current_user
    
    return permission_dependency
