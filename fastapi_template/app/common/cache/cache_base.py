"""
# File: fastapi_template/app/common/cache/cache_base.py
# Description: 캐시 백엔드 추상 클래스 및 유틸리티 함수
"""

import json
import pickle
import base64
from abc import ABC, abstractmethod
from functools import wraps
from typing import Any, Callable, Dict, Optional, TypeVar, Union, cast

from fastapi import Depends, Request
from pydantic import BaseModel

T = TypeVar("T")


class CacheBackend(ABC):
    """
    캐시 백엔드 추상 클래스
    모든 캐시 구현은 이 클래스를 상속해야 함
    """

    @abstractmethod
    async def get(self, key: str) -> Optional[str]:
        """
        캐시에서 값 조회
        """
        pass

    @abstractmethod
    async def set(self, key: str, value: str, ttl: Optional[int] = None) -> None:
        """
        캐시에 값 저장
        """
        pass

    @abstractmethod
    async def delete(self, key: str) -> None:
        """
        캐시에서 키 삭제
        """
        pass

    @abstractmethod
    async def clear_pattern(self, pattern: str) -> None:
        """
        패턴과 일치하는 모든 키 삭제
        """
        pass


def cache_key_builder(prefix: str, *args, **kwargs) -> str:
    """
    캐시 키 생성 유틸리티

    Args:
        prefix: 캐시 키 접두사
        *args: 위치 인자
        **kwargs: 키워드 인자

    Returns:
        str: 생성된 캐시 키
    """
    key_parts = [prefix]

    # 위치 인자 처리
    if args:
        key_parts.extend([str(arg) for arg in args])

    # 키워드 인자 처리 (정렬하여 일관성 유지)
    if kwargs:
        key_parts.extend([f"{k}:{kwargs[k]}" for k in sorted(kwargs.keys())])

    return ":".join(key_parts)


def serialize_value(value: Any) -> str:
    """
    값을 문자열로 직렬화

    Args:
        value: 직렬화할 값

    Returns:
        str: 직렬화된 문자열
    """
    if isinstance(value, (dict, list, str, int, float, bool)):
        # 기본 타입은 JSON으로 직렬화
        return json.dumps(value)
    elif isinstance(value, BaseModel):
        # Pydantic 모델은 JSON으로 직렬화
        return value.model_dump_json()
    else:
        # 그 외는 pickle로 직렬화 후 base64로 인코딩하여 문자열로 저장
        pickled_data = pickle.dumps(value)
        return base64.b64encode(pickled_data).decode("utf-8")


def deserialize_value(value: str) -> Any:
    """
    문자열에서 값 역직렬화

    Args:
        value: 역직렬화할 문자열 값

    Returns:
        Any: 역직렬화된 값
    """
    try:
        # JSON 역직렬화 시도
        return json.loads(value)
    except json.JSONDecodeError:
        try:
            # Base64 및 Pickle 역직렬화 시도
            binary_data = base64.b64decode(value.encode("utf-8"))
            return pickle.loads(binary_data)
        except (pickle.PickleError, base64.binascii.Error, EOFError):
            # 실패 시 원본 문자열 반환
            return value 