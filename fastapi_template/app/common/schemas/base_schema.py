from pydantic import BaseModel, ConfigDict
from datetime import datetime
from typing import Optional, TypeVar, Generic

T = TypeVar('T')

class BaseSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

class TimeStampMixin(BaseModel):
    created_at: datetime
    updated_at: Optional[datetime] = None

class ResponseSchema(BaseModel, Generic[T]):
    success: bool = True
    message: str = "Success"
    data: Optional[T] = None
    
    @classmethod
    def error(cls, message: str) -> "ResponseSchema":
        return cls(success=False, message=message)
        
    @classmethod
    def success(cls, data: T, message: str = "Success") -> "ResponseSchema[T]":
        return cls(data=data, message=message) 