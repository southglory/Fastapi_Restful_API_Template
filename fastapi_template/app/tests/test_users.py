"""
# File: fastapi_template/app/tests/test_users.py
# Description: 사용자 관련 API 테스트
# - 엔드포인트 테스트
# - 인증 테스트
# - 데이터베이스 작업 테스트
"""

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.common.auth import create_access_token
from app.common.database import get_db
from app.main import app
from app.services.user_service import UserService

# 테스트 클라이언트 생성
client = TestClient(app)

# 테스트를 위한 의존성 오버라이드
async def override_get_db():
    """테스트용 DB 세션 제공"""
    # 여기서는 실제 구현을 생략하고 테스트를 위한 예시만 제공합니다.
    # 실제 테스트에서는 테스트 데이터베이스를 설정해야 합니다.
    yield AsyncSession()

app.dependency_overrides[get_db] = override_get_db

# 테스트 시작
def test_create_user():
    """사용자 생성 테스트"""
    # 테스트 코드 구현
    pass

def test_read_user():
    """사용자 조회 테스트"""
    # 테스트 코드 구현
    pass

 