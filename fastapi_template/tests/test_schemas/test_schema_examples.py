"""
# File: tests/test_schemas/test_schema_examples.py
# Description: 스키마 예제 클래스 테스트
"""

import pytest
from datetime import datetime
from pydantic import ValidationError
from typing import Dict, Any

from app.common.schemas.schema_examples import (
    UserCreateSchema,
    UserUpdateSchema,
    UserReadSchema,
    UserServiceSchema,
    UserCreatedEvent,
)


class TestUserCreateSchema:
    """사용자 생성 스키마 테스트"""
    
    def test_valid_user_create(self):
        """유효한 사용자 생성 데이터 테스트"""
        # 유효한 데이터로 스키마 생성
        user_data = {
            "username": "testuser",
            "email": "test@example.com",
            "password": "securepass123",
            "full_name": "Test User"
        }
        user = UserCreateSchema(**user_data)
        
        # 값 검증
        assert user.username == "testuser"
        assert user.email == "test@example.com"
        assert user.password == "securepass123"
        assert user.full_name == "Test User"
        
        # 스키마 타입 검증
        assert UserCreateSchema.schema_type == "create"
        
        # 선택적 필드 생략 테스트
        minimal_user = UserCreateSchema(
            username="minuser",
            email="min@example.com",
            password="minimalpass"
        )
        assert minimal_user.full_name is None
    
    def test_invalid_user_create(self):
        """잘못된 사용자 생성 데이터 테스트"""
        # 필수 필드 누락
        with pytest.raises(ValidationError) as exc:
            UserCreateSchema(username="user1", email="test@example.com")  # password 누락
        
        errors = exc.value.errors()
        assert any("password" in str(e) for e in errors)
        
        # 이메일 형식 오류
        with pytest.raises(ValidationError) as exc:
            UserCreateSchema(
                username="user1",
                email="invalid-email",  # 유효하지 않은 이메일
                password="pass123"
            )
        
        errors = exc.value.errors()
        assert any("email" in str(e) for e in errors)
        
        # 사용자 이름 길이 제한
        with pytest.raises(ValidationError) as exc:
            UserCreateSchema(
                username="ab",  # 3자 미만
                email="test@example.com",
                password="pass123"
            )
        
        errors = exc.value.errors()
        assert any("username" in str(e) for e in errors)
        
        # 비밀번호 길이 제한
        with pytest.raises(ValidationError) as exc:
            UserCreateSchema(
                username="user1",
                email="test@example.com",
                password="short"  # 8자 미만
            )
        
        errors = exc.value.errors()
        assert any("password" in str(e) for e in errors)


class TestUserUpdateSchema:
    """사용자 업데이트 스키마 테스트"""
    
    def test_user_update_all_fields(self):
        """모든 필드 업데이트 테스트"""
        # 모든 필드를 포함한 업데이트
        update_data = {
            "username": "updateduser",
            "email": "updated@example.com",
            "full_name": "Updated User",
            "is_active": False
        }
        update = UserUpdateSchema(**update_data)
        
        # 값 검증
        assert update.username == "updateduser"
        assert update.email == "updated@example.com"
        assert update.full_name == "Updated User"
        assert update.is_active is False
        
        # 스키마 타입 검증
        assert UserUpdateSchema.schema_type == "update"
    
    def test_user_update_partial(self):
        """부분 업데이트 테스트"""
        # 일부 필드만 업데이트
        update = UserUpdateSchema(username="newname")
        
        # 제공된 필드만 설정되고 나머지는 None
        assert update.username == "newname"
        assert update.email is None
        assert update.full_name is None
        assert update.is_active is None
        
        # 다른 필드 조합
        update = UserUpdateSchema(full_name="Full Name", is_active=True)
        assert update.username is None
        assert update.email is None
        assert update.full_name == "Full Name"
        assert update.is_active is True

    def test_user_update_validation(self):
        """업데이트 유효성 검증 테스트"""
        # 이메일 형식 오류
        with pytest.raises(ValidationError) as exc:
            UserUpdateSchema(email="invalid-email")
        
        errors = exc.value.errors()
        assert any("email" in str(e) for e in errors)
        
        # 사용자 이름 길이 제한
        with pytest.raises(ValidationError) as exc:
            UserUpdateSchema(username="a")  # 3자 미만
        
        errors = exc.value.errors()
        assert any("username" in str(e) for e in errors)


class TestUserReadSchema:
    """사용자 응답 스키마 테스트"""
    
    def test_user_read_schema(self):
        """사용자 응답 스키마 테스트"""
        now = datetime.now()
        # 사용자 응답 데이터
        user_data = {
            "id": 1,
            "username": "testuser",
            "email": "test@example.com",
            "full_name": "Test User",
            "is_active": True,
            "created_at": now,
            "updated_at": now
        }
        user = UserReadSchema(**user_data)
        
        # 값 검증
        assert user.id == 1
        assert user.username == "testuser"
        assert user.email == "test@example.com"
        assert user.full_name == "Test User"
        assert user.is_active is True
        assert user.created_at == now
        assert user.updated_at == now
        
        # 스키마 타입 검증
        assert UserReadSchema.schema_type == "read"
    
    def test_user_read_schema_defaults(self):
        """사용자 응답 스키마 기본값 테스트"""
        now = datetime.now()
        # 필수 필드만 포함
        user = UserReadSchema(
            id=1,
            username="testuser",
            email="test@example.com",
            created_at=now
        )
        
        # 기본값 검증
        assert user.id == 1
        assert user.username == "testuser"
        assert user.email == "test@example.com"
        assert user.full_name is None
        assert user.is_active is True  # 기본값
        assert user.created_at == now
        assert user.updated_at is None


class TestUserServiceSchema:
    """사용자 서비스 스키마 테스트"""
    
    def test_user_service_schema(self):
        """사용자 서비스 스키마 테스트"""
        now = datetime.now()
        # 서비스 스키마 데이터 (내부 필드 포함)
        service_data = {
            "id": 1,
            "username": "testuser",
            "email": "test@example.com",
            "full_name": "Test User",
            "is_active": True,
            "hashed_password": "hashed_secret_value",
            "login_attempts": 3,
            "last_login": now,
            "permissions": ["read", "write"],
            "created_at": now,
            "updated_at": now
        }
        service = UserServiceSchema(**service_data)
        
        # 값 검증
        assert service.id == 1
        assert service.username == "testuser"
        assert service.email == "test@example.com"
        assert service.full_name == "Test User"
        assert service.is_active is True
        assert service.hashed_password == "hashed_secret_value"
        assert service.login_attempts == 3
        assert service.last_login == now
        assert service.permissions == ["read", "write"]
        assert service.created_at == now
        assert service.updated_at == now
        
        # 스키마 타입 검증
        assert UserServiceSchema.schema_type == "service"
    
    def test_user_service_schema_defaults(self):
        """사용자 서비스 스키마 기본값 테스트"""
        now = datetime.now()
        # 최소 필수 필드만 포함
        service = UserServiceSchema(
            id=1,
            username="testuser",
            email="test@example.com",
            hashed_password="hashed_secret",
            created_at=now
        )
        
        # 기본값 검증
        assert service.id == 1
        assert service.username == "testuser"
        assert service.email == "test@example.com"
        assert service.full_name is None
        assert service.is_active is True  # 기본값
        assert service.hashed_password == "hashed_secret"
        assert service.login_attempts == 0  # 기본값
        assert service.last_login is None
        assert service.permissions == []  # 기본값
        assert service.created_at == now
        assert service.updated_at is None


class TestUserCreatedEvent:
    """사용자 생성 이벤트 테스트"""
    
    def test_user_created_event(self):
        """사용자 생성 이벤트 테스트"""
        now = datetime.now()
        # 이벤트 페이로드
        payload = {
            "user_id": 1,
            "username": "newuser",
            "email": "new@example.com"
        }
        
        # 이벤트 인스턴스 생성
        event = UserCreatedEvent(timestamp=now, payload=payload)
        
        # 값 검증
        assert event.event_type == "user.created"  # 기본값
        assert event.timestamp == now
        assert event.payload == payload
        
        # 스키마 타입 검증
        assert UserCreatedEvent.schema_type == "event"
    
    def test_user_created_event_default_timestamp(self):
        """사용자 생성 이벤트 기본 타임스탬프 테스트"""
        # 타임스탬프 없이 생성
        payload = {"user_id": 1}
        event = UserCreatedEvent(payload=payload)
        
        # 현재 시간이 자동으로 설정되는지 확인
        assert isinstance(event.timestamp, datetime)
        # 현재 시간과 큰 차이가 없는지 확인
        time_diff = datetime.now() - event.timestamp
        assert time_diff.total_seconds() < 5  # 5초 이내 