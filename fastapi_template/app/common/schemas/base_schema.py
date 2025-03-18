"""
# File: fastapi_template/app/common/schemas/base_schema.py
# Description: 스키마 기본 클래스 및 타입 정의
# - 데이터 흐름 방향 및 사용 목적별 스키마 구분
# - 공통 응답 형식 정의
"""

from pydantic import BaseModel, ConfigDict
from datetime import datetime
from typing import Optional, TypeVar, Generic, ClassVar, Dict, Any, List

T = TypeVar("T")


class BaseSchema(BaseModel):
    """모든 스키마의 기본 클래스"""

    model_config = ConfigDict(from_attributes=True)

    # 스키마 특성 표시를 위한 클래스 변수
    schema_type: ClassVar[str] = "base"


# 데이터 흐름 방향에 따른 스키마 분류
class InputSchema(BaseSchema):
    """외부에서 시스템으로 들어오는 데이터 스키마"""

    schema_type: ClassVar[str] = "input"


class OutputSchema(BaseSchema):
    """시스템에서 외부로 나가는 데이터 스키마"""

    schema_type: ClassVar[str] = "output"


class InternalSchema(BaseSchema):
    """시스템 내부에서만 사용되는 데이터 스키마"""

    schema_type: ClassVar[str] = "internal"


# 데이터 생명주기(CRUD)에 따른 스키마 분류
class CreateSchema(InputSchema):
    """생성 작업을 위한 스키마 (POST)"""

    schema_type: ClassVar[str] = "create"


class ReadSchema(OutputSchema):
    """조회 작업을 위한 스키마 (GET)"""

    schema_type: ClassVar[str] = "read"


class UpdateSchema(InputSchema):
    """업데이트 작업을 위한 스키마 (PUT/PATCH)"""

    schema_type: ClassVar[str] = "update"


# 서비스 간 통신을 위한 스키마
class ServiceSchema(InternalSchema):
    """서비스 레이어 간 통신을 위한 스키마"""

    schema_type: ClassVar[str] = "service"


class EventSchema(InternalSchema):
    """이벤트 메시지를 위한 스키마"""

    schema_type: ClassVar[str] = "event"
    event_type: str
    timestamp: datetime = datetime.now()
    payload: Dict[str, Any]


class TimeStampMixin(BaseModel):
    """타임스탬프 필드 믹스인"""

    created_at: datetime
    updated_at: Optional[datetime] = None


class ResponseSchema(BaseModel, Generic[T]):
    """API 응답을 위한 표준 스키마"""

    is_success: bool = True
    message: str = "Success"
    data: Optional[T] = None
    error_code: Optional[str] = None

    @classmethod
    def error(cls, message: str, error_code: Optional[str] = None) -> "ResponseSchema":
        """오류 응답 생성"""
        return cls(is_success=False, message=message, error_code=error_code)

    @classmethod
    def success(
        cls, data: Optional[T] = None, message: str = "Success"
    ) -> "ResponseSchema[T]":
        """성공 응답 생성"""
        return cls(is_success=True, data=data, message=message)
