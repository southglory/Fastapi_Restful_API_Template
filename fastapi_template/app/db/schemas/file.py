"""
# File: fastapi_template/app/db/schemas/file.py
# Description: 파일 관련 스키마 정의
"""

from typing import Optional
from datetime import datetime
from pydantic import BaseModel, Field, validator


class FileBase(BaseModel):
    """파일 기본 스키마"""
    name: str = Field(..., description="파일 이름")
    path: str = Field(..., description="파일 경로")
    type: str = Field(..., description="파일 타입 (예: image, document, video)")
    mime_type: str = Field(..., description="MIME 타입")
    size: Optional[int] = Field(None, description="파일 크기 (바이트)")
    user_id: Optional[int] = Field(None, description="소유자 ID")


class FileCreate(FileBase):
    """파일 생성 스키마"""
    pass


class FileUpdate(BaseModel):
    """파일 수정 스키마"""
    name: Optional[str] = Field(None, description="파일 이름")
    path: Optional[str] = Field(None, description="파일 경로")
    type: Optional[str] = Field(None, description="파일 타입")
    mime_type: Optional[str] = Field(None, description="MIME 타입")
    size: Optional[int] = Field(None, description="파일 크기 (바이트)")
    user_id: Optional[int] = Field(None, description="소유자 ID")


class FileInDBBase(FileBase):
    """데이터베이스 파일 기본 스키마"""
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True


class File(FileInDBBase):
    """API 응답용 파일 스키마"""
    pass


class FileInDB(FileInDBBase):
    """데이터베이스 파일 스키마"""
    pass 