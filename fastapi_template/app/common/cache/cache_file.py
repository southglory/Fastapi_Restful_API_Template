"""
# File: fastapi_template/app/common/cache/cache_file.py
# Description: 파일 시스템 기반 캐시 구현
"""

import os
import json
import time
import hashlib
import glob
import asyncio
from typing import Any, Dict, Optional, Tuple

from fastapi_template.app.common.config import config_settings
from fastapi_template.app.common.cache.cache_base import CacheBackend


class FileCacheBackend(CacheBackend):
    """
    파일 시스템 캐시 백엔드 클래스
    
    이 구현은 디스크에 캐시 데이터를 저장합니다.
    서버 재시작 후에도 캐시가 유지됩니다.
    """

    def __init__(
        self,
        cache_dir: str = None,
        ttl: int = config_settings.REDIS_TTL
    ):
        """
        초기화
        
        Args:
            cache_dir: 캐시 디렉토리 경로
            ttl: 캐시 유효기간 (초)
        """
        self.ttl = ttl
        self.cache_dir = cache_dir or os.path.join(
            os.path.dirname(os.path.abspath(__file__)),
            "..", "..", "..", ".cache"
        )
        
        # 캐시 디렉토리 생성
        os.makedirs(self.cache_dir, exist_ok=True)
        
    def _get_file_path(self, key: str) -> str:
        """
        캐시 키에 대한 파일 경로 반환
        
        Args:
            key: 캐시 키
            
        Returns:
            str: 파일 경로
        """
        # 키를 해시값으로 변환 (파일 이름으로 사용하기 위함)
        hashed_key = hashlib.md5(key.encode()).hexdigest()
        return os.path.join(self.cache_dir, f"{hashed_key}.cache")
        
    def _read_cache_file(self, file_path: str) -> Tuple[Optional[str], bool]:
        """
        캐시 파일 읽기
        
        Args:
            file_path: 파일 경로
            
        Returns:
            Tuple[Optional[str], bool]: (캐시 값, 유효성)
        """
        try:
            if not os.path.exists(file_path):
                return None, False
                
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                
            # 만료 시간 확인
            expires_at = data.get('expires_at')
            if expires_at is not None and expires_at < time.time():
                # 만료된 캐시 파일 삭제
                os.remove(file_path)
                return None, False
                
            return data.get('value'), True
        except (json.JSONDecodeError, IOError):
            # 파일이 손상되었거나 읽을 수 없는 경우
            if os.path.exists(file_path):
                os.remove(file_path)
            return None, False
            
    def _write_cache_file(self, file_path: str, value: str, expires_at: Optional[float]) -> bool:
        """
        캐시 파일 쓰기
        
        Args:
            file_path: 파일 경로
            value: 캐시 값
            expires_at: 만료 시간
            
        Returns:
            bool: 성공 여부
        """
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump({
                    'value': value,
                    'expires_at': expires_at
                }, f)
            return True
        except IOError:
            return False
    
    async def get(self, key: str) -> Optional[str]:
        """
        캐시에서 값 조회
        
        Args:
            key: 캐시 키
            
        Returns:
            Optional[str]: 조회된 값 또는 None
        """
        file_path = self._get_file_path(key)
        # I/O 작업은 비동기로 실행
        loop = asyncio.get_event_loop()
        value, valid = await loop.run_in_executor(None, self._read_cache_file, file_path)
        return value if valid else None

    async def set(self, key: str, value: str, ttl: Optional[int] = None) -> None:
        """
        캐시에 값 저장
        
        Args:
            key: 캐시 키
            value: 저장할 값
            ttl: 유효기간 (초)
        """
        file_path = self._get_file_path(key)
        expires_at = None
        if ttl is not None or self.ttl is not None:
            expires_at = time.time() + (ttl or self.ttl)
            
        # I/O 작업은 비동기로 실행
        loop = asyncio.get_event_loop()
        await loop.run_in_executor(None, self._write_cache_file, file_path, value, expires_at)

    async def delete(self, key: str) -> None:
        """
        캐시에서 키 삭제
        
        Args:
            key: 삭제할 캐시 키
        """
        file_path = self._get_file_path(key)
        # I/O 작업은 비동기로 실행
        loop = asyncio.get_event_loop()
        
        def _delete():
            if os.path.exists(file_path):
                os.remove(file_path)
                
        await loop.run_in_executor(None, _delete)

    async def clear_pattern(self, pattern: str) -> None:
        """
        패턴과 일치하는 모든 키 삭제
        
        참고: 이 구현은 효율적이지 않을 수 있습니다.
        파일 시스템에서는 패턴 매칭이 제한적이기 때문입니다.
        
        Args:
            pattern: 키 패턴 (예: "user:*")
        """
        # 모든 캐시 파일 경로
        cache_files = glob.glob(os.path.join(self.cache_dir, "*.cache"))
        
        # I/O 작업은 비동기로 실행
        loop = asyncio.get_event_loop()
        
        def _check_and_delete_files():
            for file_path in cache_files:
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                    
                    # 각 파일에 키 정보 저장이 필요
                    # 현재 구현에서는 패턴 기반 삭제가 제한적임
                    # 실제 구현 시 메타데이터 저장 필요
                    
                    # 임시 방편: 모든 캐시 삭제
                    if pattern == "*":
                        os.remove(file_path)
                except:
                    # 오류 발생 시 파일 삭제
                    if os.path.exists(file_path):
                        os.remove(file_path)
        
        await loop.run_in_executor(None, _check_and_delete_files) 