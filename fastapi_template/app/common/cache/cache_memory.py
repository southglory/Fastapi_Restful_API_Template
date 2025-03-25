"""
# File: fastapi_template/app/common/cache/cache_memory.py
# Description: 인메모리 캐시 구현
"""

import re
import time
from typing import Any, Dict, Optional, Pattern, Tuple

from fastapi_template.app.common.config import config_settings
from fastapi_template.app.common.cache.cache_base import CacheBackend


class MemoryCacheBackend(CacheBackend):
    """
    인메모리 캐시 백엔드 클래스
    
    주의: 이 구현은 단일 프로세스에서만 동작합니다.
    서버 재시작 시 모든 캐시가 초기화됩니다.
    """

    # 클래스 변수로 캐시 저장소 정의 (싱글톤 패턴)
    _cache: Dict[str, Tuple[str, Optional[float]]] = {}
    
    def __init__(self, ttl: int = config_settings.REDIS_TTL):
        """
        초기화
        
        Args:
            ttl: 캐시 유효기간 (초)
        """
        self.ttl = ttl
        
    def _clean_expired(self):
        """만료된 항목 정리"""
        now = time.time()
        expired_keys = [
            key for key, (_, expires_at) in self._cache.items()
            if expires_at is not None and expires_at < now
        ]
        for key in expired_keys:
            del self._cache[key]
            
    async def get(self, key: str) -> Optional[str]:
        """
        캐시에서 값 조회
        
        Args:
            key: 캐시 키
            
        Returns:
            Optional[str]: 조회된 값 또는 None
        """
        self._clean_expired()
        if key in self._cache:
            value, expires_at = self._cache[key]
            if expires_at is None or expires_at > time.time():
                return value
            # 만료된 항목 삭제
            del self._cache[key]
        return None

    async def set(self, key: str, value: str, ttl: Optional[int] = None) -> None:
        """
        캐시에 값 저장
        
        Args:
            key: 캐시 키
            value: 저장할 값
            ttl: 유효기간 (초) - None이면 무기한 유지
        """
        expires_at = None
        if ttl is not None:
            # ttl 파라미터가 명시적으로 설정된 경우
            expires_at = time.time() + ttl
        elif self.ttl is not None and ttl is None:
            # ttl 파라미터는 None이지만 기본 ttl은 설정된 경우 (기본값 사용)
            expires_at = time.time() + self.ttl
        
        # expires_at이 None이면 무기한 유지
        self._cache[key] = (value, expires_at)

    async def delete(self, key: str) -> None:
        """
        캐시에서 키 삭제
        
        Args:
            key: 삭제할 캐시 키
        """
        if key in self._cache:
            del self._cache[key]

    async def clear_pattern(self, pattern: str) -> None:
        """
        패턴과 일치하는 모든 키 삭제
        
        Args:
            pattern: 키 패턴 (예: "user:*")
        """
        # Redis 와일드카드를 정규 표현식으로 변환
        regex_pattern = pattern.replace("*", ".*")
        compiled_pattern = re.compile(f"^{regex_pattern}$")
        
        # 패턴과 일치하는 키 찾기
        keys_to_delete = [
            key for key in self._cache.keys()
            if compiled_pattern.match(key)
        ]
        
        # 키 삭제
        for key in keys_to_delete:
            del self._cache[key] 