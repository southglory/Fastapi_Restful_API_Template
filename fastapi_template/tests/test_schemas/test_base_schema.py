"""
# File: tests/test_schemas/test_base_schema.py
# Description: 기본 스키마 클래스 테스트
"""

import pytest
from datetime import datetime
from pydantic import BaseModel
from typing import Dict, Any, List, Optional

from app.common.schemas.base_schema import (
    BaseSchema,
    InputSchema,
    OutputSchema,
    InternalSchema,
    CreateSchema,
    ReadSchema,
    UpdateSchema,
    ServiceSchema,
    EventSchema,
    TimeStampMixin,
    ResponseSchema,
)


class TestBaseSchema:
    """기본 스키마 클래스 테스트"""

    def test_base_schema_attributes(self):
        """BaseSchema 속성 테스트"""
        # 기본 스키마 인스턴스 생성
        class SampleSchema(BaseSchema):
            name: str
            value: int

        sample = SampleSchema(name="test", value=10)
        
        # 값 검증
        assert sample.name == "test"
        assert sample.value == 10
        
        # 메타데이터 검증
        assert SampleSchema.schema_type == "base"
        
        # from_attributes 설정 검증
        assert SampleSchema.model_config["from_attributes"] is True

    def test_schema_hierarchy(self):
        """스키마 계층 구조 테스트"""
        # 각 스키마 유형별 계층 구조 확인
        assert issubclass(InputSchema, BaseSchema)
        assert issubclass(OutputSchema, BaseSchema)
        assert issubclass(InternalSchema, BaseSchema)
        
        assert issubclass(CreateSchema, InputSchema)
        assert issubclass(UpdateSchema, InputSchema)
        assert issubclass(ReadSchema, OutputSchema)
        
        assert issubclass(ServiceSchema, InternalSchema)
        assert issubclass(EventSchema, InternalSchema)
        
        # 스키마 타입 검증
        assert InputSchema.schema_type == "input"
        assert OutputSchema.schema_type == "output"
        assert InternalSchema.schema_type == "internal"
        assert CreateSchema.schema_type == "create"
        assert ReadSchema.schema_type == "read"
        assert UpdateSchema.schema_type == "update"
        assert ServiceSchema.schema_type == "service"
        assert EventSchema.schema_type == "event"


class TestEventSchema:
    """이벤트 스키마 테스트"""
    
    def test_event_schema_attributes(self):
        """EventSchema 속성 테스트"""
        # 현재 시간
        now = datetime.now()
        
        # 이벤트 스키마 인스턴스 생성
        event = EventSchema(
            event_type="test.event",
            timestamp=now,
            payload={"id": 1, "message": "테스트 이벤트"}
        )
        
        # 값 검증
        assert event.event_type == "test.event"
        assert event.timestamp == now
        assert event.payload == {"id": 1, "message": "테스트 이벤트"}
    
    def test_event_schema_default_timestamp(self):
        """EventSchema 기본 타임스탬프 테스트"""
        # 타임스탬프를 지정하지 않고 이벤트 생성
        event = EventSchema(
            event_type="test.event",
            payload={"id": 1}
        )
        
        # 현재 시간이 자동으로 설정되는지 확인
        assert isinstance(event.timestamp, datetime)
        # 현재 시간과 큰 차이가 없는지 확인
        time_diff = datetime.now() - event.timestamp
        assert time_diff.total_seconds() < 5  # 5초 이내


class TestTimeStampMixin:
    """타임스탬프 믹스인 테스트"""
    
    def test_timestamp_mixin_attributes(self):
        """TimeStampMixin 속성 테스트"""
        # 믹스인을 사용한 스키마 정의
        class TimedSchema(BaseSchema, TimeStampMixin):
            name: str
        
        # 인스턴스 생성
        now = datetime.now()
        timed = TimedSchema(name="test", created_at=now, updated_at=now)
        
        # 값 검증
        assert timed.name == "test"
        assert timed.created_at == now
        assert timed.updated_at == now
    
    def test_timestamp_mixin_optional_fields(self):
        """TimeStampMixin 선택적 필드 테스트"""
        # 믹스인을 사용한 스키마 정의
        class TimedSchema(BaseSchema, TimeStampMixin):
            name: str
        
        # updated_at 없이 인스턴스 생성
        now = datetime.now()
        timed = TimedSchema(name="test", created_at=now)
        
        # 값 검증
        assert timed.name == "test"
        assert timed.created_at == now
        assert timed.updated_at is None


class TestResponseSchema:
    """응답 스키마 테스트"""
    
    def test_response_schema_default_values(self):
        """ResponseSchema 기본값 테스트"""
        # 기본 응답 스키마 생성
        response = ResponseSchema()
        
        # 기본값 검증
        assert response.is_success is True
        assert response.message == "Success"
        assert response.data is None
        assert response.error_code is None
    
    def test_response_schema_with_data(self):
        """ResponseSchema 데이터 포함 테스트"""
        # 데이터를 포함한 응답 스키마 생성
        data = {"id": 1, "name": "테스트"}
        response = ResponseSchema(data=data, message="데이터 조회 성공")
        
        # 값 검증
        assert response.is_success is True
        assert response.message == "데이터 조회 성공"
        assert response.data == data
        assert response.error_code is None
    
    def test_response_schema_with_generics(self):
        """ResponseSchema 제네릭 타입 테스트"""
        # 제네릭 타입을 사용한 응답 스키마 정의
        class UserModel(BaseModel):
            id: int
            name: str
        
        # 타입 힌트가 있는 응답 생성
        user = UserModel(id=1, name="사용자")
        response = ResponseSchema[UserModel](data=user)
        
        # 값 검증
        assert response.is_success is True
        assert response.data.id == 1
        assert response.data.name == "사용자"
    
    def test_response_schema_error_method(self):
        """ResponseSchema error 메서드 테스트"""
        # error 메서드를 사용한 오류 응답 생성
        error_response = ResponseSchema.error(
            message="요청 처리 중 오류가 발생했습니다", 
            error_code="E1001"
        )
        
        # 값 검증
        assert error_response.is_success is False
        assert error_response.message == "요청 처리 중 오류가 발생했습니다"
        assert error_response.error_code == "E1001"
        assert error_response.data is None
    
    def test_response_schema_success_method(self):
        """ResponseSchema success 메서드 테스트"""
        # success 메서드를 사용한 성공 응답 생성
        data = {"result": "성공"}
        success_response = ResponseSchema.success(
            data=data,
            message="작업이 성공적으로 완료되었습니다"
        )
        
        # 값 검증
        assert success_response.is_success is True
        assert success_response.message == "작업이 성공적으로 완료되었습니다"
        assert success_response.data == data
        assert success_response.error_code is None 