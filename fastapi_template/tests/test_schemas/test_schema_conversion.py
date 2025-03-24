"""
# File: tests/test_schemas/test_schema_conversion.py
# Description: 스키마 변환 테스트
"""

import pytest
from datetime import datetime
from dataclasses import dataclass
from pydantic import ValidationError

from app.common.schemas.base_schema import (
    BaseSchema,
    ResponseSchema,
)

from app.common.schemas.schema_examples import (
    UserCreateSchema,
    UserReadSchema,
    UserServiceSchema,
)


# 테스트를 위한 가상 데이터베이스 모델
@dataclass
class UserDBModel:
    """테스트용 사용자 DB 모델"""
    id: int
    username: str
    email: str
    hashed_password: str
    full_name: str = None
    is_active: bool = True
    created_at: datetime = None
    updated_at: datetime = None
    login_attempts: int = 0
    permissions: list = None


class TestSchemaConversion:
    """스키마 변환 테스트"""
    
    def test_db_model_to_service_schema(self):
        """DB 모델을 서비스 스키마로 변환 테스트"""
        # 테스트 DB 모델 인스턴스 생성
        now = datetime.now()
        db_model = UserDBModel(
            id=1,
            username="testuser",
            email="test@example.com",
            hashed_password="hashed_value",
            full_name="Test User",
            is_active=True,
            created_at=now,
            updated_at=now,
            login_attempts=2,
            permissions=["read"]
        )
        
        # 모델을 스키마로 변환
        service_schema = UserServiceSchema.model_validate(db_model)
        
        # 변환된 스키마 검증
        assert service_schema.id == db_model.id
        assert service_schema.username == db_model.username
        assert service_schema.email == db_model.email
        assert service_schema.hashed_password == db_model.hashed_password
        assert service_schema.full_name == db_model.full_name
        assert service_schema.is_active == db_model.is_active
        assert service_schema.created_at == db_model.created_at
        assert service_schema.updated_at == db_model.updated_at
        assert service_schema.login_attempts == db_model.login_attempts
        assert service_schema.permissions == db_model.permissions
    
    def test_service_schema_to_read_schema(self):
        """서비스 스키마를 응답 스키마로 변환 테스트"""
        # 서비스 스키마 인스턴스 생성
        now = datetime.now()
        service_schema = UserServiceSchema(
            id=1,
            username="testuser",
            email="test@example.com",
            hashed_password="hashed_secret",
            full_name="Test User",
            is_active=True,
            created_at=now,
            updated_at=now,
            login_attempts=5,
            last_login=now,
            permissions=["read", "write"]
        )
        
        # 서비스 스키마를 응답 스키마로 변환
        read_schema = UserReadSchema.model_validate(service_schema)
        
        # 변환된 응답 스키마 검증
        assert read_schema.id == service_schema.id
        assert read_schema.username == service_schema.username
        assert read_schema.email == service_schema.email
        assert read_schema.full_name == service_schema.full_name
        assert read_schema.is_active == service_schema.is_active
        assert read_schema.created_at == service_schema.created_at
        assert read_schema.updated_at == service_schema.updated_at
        
        # 응답 스키마에는 내부 필드가 제외되었는지 확인
        with pytest.raises(AttributeError):
            read_schema.hashed_password
        with pytest.raises(AttributeError):
            read_schema.login_attempts
        with pytest.raises(AttributeError):
            read_schema.last_login
        with pytest.raises(AttributeError):
            read_schema.permissions
    
    def test_create_schema_validation(self):
        """생성 스키마 데이터 유효성 검증 테스트"""
        # 유효한 생성 데이터
        valid_data = {
            "username": "newuser",
            "email": "new@example.com",
            "password": "securepass",
            "full_name": "New User"
        }
        
        # 유효한 데이터로 스키마 생성
        create_schema = UserCreateSchema(**valid_data)
        
        # 스키마 유효성 검증
        assert create_schema.username == valid_data["username"]
        assert create_schema.email == valid_data["email"]
        assert create_schema.password == valid_data["password"]
        assert create_schema.full_name == valid_data["full_name"]
        
        # 잘못된 데이터로 스키마 생성 시도
        invalid_data = {
            "username": "u",  # 3자 미만
            "email": "invalid-email",
            "password": "short",  # 8자 미만
        }
        
        # 유효성 검증 오류 확인
        with pytest.raises(ValidationError) as exc:
            UserCreateSchema(**invalid_data)
        
        # 오류 메시지 확인
        errors = exc.value.errors()
        assert len(errors) > 0
        assert any("username" in str(e) for e in errors)
        assert any("email" in str(e) for e in errors)
        assert any("password" in str(e) for e in errors)


class TestResponseSchemaConversion:
    """응답 스키마 변환 테스트"""
    
    def test_response_schema_with_schema_data(self):
        """스키마 데이터를 포함한 응답 테스트"""
        # 사용자 읽기 스키마 생성
        now = datetime.now()
        user = UserReadSchema(
            id=1,
            username="testuser",
            email="test@example.com",
            full_name="Test User",
            created_at=now
        )
        
        # 응답 스키마에 데이터 포함
        response = ResponseSchema(
            is_success=True,
            message="사용자 조회 성공",
            data=user
        )
        
        # 응답 스키마 검증
        assert response.is_success is True
        assert response.message == "사용자 조회 성공"
        assert response.data == user
        assert response.data.id == 1
        assert response.data.username == "testuser"
        assert response.data.email == "test@example.com"
        assert response.data.full_name == "Test User"
        assert response.data.created_at == now
    
    def test_response_schema_dict_conversion(self):
        """응답 스키마 딕셔너리 변환 테스트"""
        # 데이터 포함 응답 생성
        data = {"id": 1, "name": "Test"}
        response = ResponseSchema(
            is_success=True,
            message="Success",
            data=data
        )
        
        # 딕셔너리로 변환
        response_dict = response.model_dump()
        
        # 변환 결과 검증
        assert isinstance(response_dict, dict)
        assert response_dict["is_success"] is True
        assert response_dict["message"] == "Success"
        assert response_dict["data"] == data
        assert response_dict["error_code"] is None
    
    def test_response_schema_json_conversion(self):
        """응답 스키마 JSON 변환 테스트"""
        # 응답 생성
        response = ResponseSchema(
            is_success=True,
            message="Success",
            data={"id": 1, "name": "Test"}
        )
        
        # JSON으로 변환
        json_str = response.model_dump_json()
        
        # JSON 문자열 검증
        assert isinstance(json_str, str)
        assert '"is_success":true' in json_str.replace(" ", "")
        assert '"message":"Success"' in json_str.replace(" ", "")
        assert '"data":{"id":1,"name":"Test"}' in json_str.replace(" ", "")
    
    def test_nested_schema_conversion(self):
        """중첩 스키마 변환 테스트"""
        # 내부 스키마 정의
        class InnerSchema(BaseSchema):
            value: str
        
        # 외부 스키마 정의
        class OuterSchema(BaseSchema):
            title: str
            inner: InnerSchema
        
        # 중첩 스키마 인스턴스 생성
        inner = InnerSchema(value="내부값")
        outer = OuterSchema(title="외부제목", inner=inner)
        
        # 응답에 중첩 스키마 포함
        response = ResponseSchema(
            data=outer,
            message="중첩 스키마 응답"
        )
        
        # 응답 검증
        assert response.data.title == "외부제목"
        assert response.data.inner.value == "내부값"
        
        # 딕셔너리 변환 검증
        response_dict = response.model_dump()
        assert response_dict["data"]["title"] == "외부제목"
        assert response_dict["data"]["inner"]["value"] == "내부값" 