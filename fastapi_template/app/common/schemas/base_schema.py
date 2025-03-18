from pydantic import BaseModel, ConfigDict
from datetime import datetime
from typing import Optional, TypeVar, Generic

T = TypeVar("T")


class BaseSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)


class TimeStampMixin(BaseModel):
    created_at: datetime
    updated_at: Optional[datetime] = None


class ResponseSchema(BaseModel, Generic[T]):
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
