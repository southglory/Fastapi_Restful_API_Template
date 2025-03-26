"""
# File: fastapi_template/app/common/repositories/__init__.py
# Description: 리포지토리 모듈 패키지
"""

from fastapi_template.app.common.repositories.repositories_base import BaseRepository
from fastapi_template.app.common.repositories.repositories_user import UserRepository
from fastapi_template.app.common.repositories.repositories_auth import AuthRepository
from fastapi_template.app.common.repositories.repository_file import FileRepository

__all__ = [
    "BaseRepository",
    "UserRepository",
    "AuthRepository",
    "FileRepository",
] 