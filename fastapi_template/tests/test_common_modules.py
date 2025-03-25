"""
# File: fastapi_template/tests/test_common_modules.py
# Description: 공통 모듈 테스트
"""

import asyncio
import json
import os
import pytest
from datetime import datetime, timedelta

# 테스트 시 import 오류 방지
from typing import Any, Awaitable, Callable, Optional

from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel

# 설정 모듈 테스트
from app.common.config import DevSettings
from fastapi_template.app.common.config import config_settings


class ConfigTest:
    """설정 모듈 테스트"""

    def test_settings(self):
        """기본 설정 로드 테스트"""
        print("\n--- 설정 모듈 테스트 ---")
        print(f"프로젝트 이름: {config_settings.PROJECT_NAME}")
        print(f"API 경로: {config_settings.API_V1_STR}")
        print(f"데이터베이스 URL: {config_settings.DATABASE_URL}")
        print(f"Redis 호스트: {config_settings.REDIS_HOST}")

        assert config_settings.PROJECT_NAME, "프로젝트 이름이 로드되지 않음"
        assert config_settings.API_V1_STR, "API 경로가 로드되지 않음"
        assert config_settings.DATABASE_URL, "데이터베이스 URL이 로드되지 않음"

        print("✅ 설정 모듈 테스트 완료")
        return True


# 인증 모듈 테스트
from app.common.auth import (
    create_access_token,
    verify_token,
    get_password_hash,
    verify_password,
)


class AuthTest:
    """인증 모듈 테스트"""

    def test_password_hashing(self):
        """비밀번호 해싱 테스트"""
        print("\n--- 비밀번호 해싱 테스트 ---")
        password = "test_password123"
        hashed = get_password_hash(password)

        print(f"원본 비밀번호: {password}")
        print(f"해시된 비밀번호: {hashed}")

        # 해시 검증
        is_valid = verify_password(password, hashed)
        print(f"비밀번호 검증 결과: {is_valid}")

        assert is_valid, "비밀번호 해싱/검증 실패"
        assert not verify_password("wrong_password", hashed), "잘못된 비밀번호가 검증됨"

        print("✅ 비밀번호 해싱 테스트 완료")
        return True

    def test_jwt_token(self):
        """JWT 토큰 테스트"""
        print("\n--- JWT 토큰 테스트 ---")
        user_id = 123

        # 토큰 생성
        token = create_access_token(subject=user_id)
        print(f"생성된 토큰: {token[:20]}...")

        # 토큰 검증
        payload = verify_token(token)
        decoded_user_id = payload.get("sub")
        print(f"디코딩된 user_id: {decoded_user_id}")

        assert decoded_user_id == str(
            user_id
        ), "토큰에서 user_id가 올바르게 디코딩되지 않음"

        # 만료 시간 테스트
        short_token = create_access_token(
            subject=user_id, expires_delta=timedelta(seconds=1)
        )
        print("1초 후 만료되는 토큰 생성")

        # 토큰이 아직 유효한지 확인
        payload = verify_token(short_token)
        assert payload.get("sub") == str(user_id), "토큰이 즉시 만료됨"

        print("✅ JWT 토큰 테스트 완료")
        return True


# 예외 처리 모듈 테스트
from app.common.exceptions import (
    AuthenticationError,
    PermissionDeniedError,
    ValidationError,
)


class ExceptionTest:
    """예외 처리 모듈 테스트"""

    def test_custom_exceptions(self):
        """사용자 정의 예외 테스트"""
        print("\n--- 사용자 정의 예외 테스트 ---")

        # 각 예외 생성 및 속성 확인
        auth_error = AuthenticationError("인증 실패")
        print(
            f"AuthenticationError - 상태 코드: {auth_error.status_code}, 메시지: {auth_error.detail}"
        )

        perm_error = PermissionDeniedError("권한 없음")
        print(
            f"PermissionDeniedError - 상태 코드: {perm_error.status_code}, 메시지: {perm_error.detail}"
        )

        val_error = ValidationError("유효하지 않은 데이터")
        print(
            f"ValidationError - 상태 코드: {val_error.status_code}, 메시지: {val_error.detail}"
        )

        # 예외 발생 테스트
        try:
            raise AuthenticationError("테스트 예외")
            assert False, "예외가 발생하지 않음"
        except AuthenticationError as e:
            print(f"발생한 예외: {type(e).__name__}, 메시지: {e.detail}")
            assert e.status_code == 401, "잘못된 상태 코드"
            assert e.detail == "테스트 예외", "잘못된 에러 메시지"

        print("✅ 사용자 정의 예외 테스트 완료")
        return True


# 스키마 모듈 테스트
from app.common.schemas.base_schema import ResponseSchema


class SchemaTest:
    """스키마 모듈 테스트"""

    def test_response_schema(self):
        """응답 스키마 테스트"""
        print("\n--- 응답 스키마 테스트 ---")

        # 성공 응답 생성
        success_data = {"id": 1, "name": "Test Item"}
        success_resp = ResponseSchema.success(data=success_data)
        print(f"성공 응답: {success_resp.model_dump_json()}")

        assert success_resp.is_success is True, "is_success 플래그가 True가 아님"
        assert success_resp.data == success_data, "응답 데이터가 일치하지 않음"

        # 오류 응답 생성
        error_resp = ResponseSchema.error(
            message="오류 발생", error_code="ITEM_NOT_FOUND"
        )
        print(f"오류 응답: {error_resp.model_dump_json()}")

        assert error_resp.is_success is False, "is_success 플래그가 False가 아님"
        assert error_resp.message == "오류 발생", "오류 메시지가 일치하지 않음"
        assert error_resp.error_code == "ITEM_NOT_FOUND", "오류 코드가 일치하지 않음"

        print("✅ 응답 스키마 테스트 완료")
        return True


# 캐싱 모듈 테스트
try:
    from app.common.cache.redis_client import cached, invalidate_cache  # noqa: F401
except ImportError:
    # 테스트 실행을 위해 더미 함수 제공
    def cache_key_builder(prefix: str, *args, **kwargs) -> str:
        """캐시 키 생성 유틸리티 더미 함수"""
        return prefix

    def cached(
        prefix: str,
        ttl: Optional[int] = None,
        key_builder: Callable = cache_key_builder,
    ):
        """캐시 데코레이터 더미 함수"""

        def decorator(func: Callable) -> Callable:
            async def wrapper(*args, **kwargs):
                return await func(*args, **kwargs)

            return wrapper

        return decorator

    def invalidate_cache(pattern: str):
        """캐시 무효화 더미 함수"""

        def decorator(func: Callable) -> Callable:
            async def wrapper(*args, **kwargs):
                result = await func(*args, **kwargs)
                return result

            return wrapper

        return decorator


# 암호화 유틸리티 테스트
from app.common.security.encryption import encrypt_data, decrypt_data


class EncryptionTest:
    """암호화 유틸리티 테스트"""

    def test_encryption(self):
        """암호화/복호화 테스트"""
        print("\n--- 암호화/복호화 테스트 ---")

        # 다양한 데이터 타입 테스트
        test_data = [
            "민감한 개인정보",
            "123456789",
            "한글 테스트 및 특수문자 !@#$%^&*()",
        ]

        for data in test_data:
            # 암호화
            encrypted = encrypt_data(data)
            print(f"원본 데이터: {data}")
            print(f"암호화된 데이터: {encrypted[:20]}...")

            # 원본과 암호화 데이터가 다른지 확인
            assert encrypted != data, "데이터가 암호화되지 않음"

            # 복호화
            decrypted = decrypt_data(encrypted)
            print(f"복호화된 데이터: {decrypted}")

            # 복호화 데이터가 원본과 일치하는지 확인
            assert decrypted == data, "복호화된 데이터가 원본과 일치하지 않음"

        print("✅ 암호화/복호화 테스트 완료")
        return True


async def run_async_tests():
    """비동기 테스트 실행"""
    print("\n--- Redis 캐싱 테스트 ---")
    print("Redis 서버가 필요하므로 테스트를 건너뜁니다.")
    print(
        "✅ 테스트를 실행하려면 Redis 서버를 설정하고 app/common/utils/cache.py 모듈을 확인하세요."
    )


def run_tests():
    """모든 테스트 실행"""
    print("\n========== 공통 모듈 테스트 시작 ==========\n")

    # 동기 테스트 실행
    config_test = ConfigTest()
    config_test.test_settings()

    auth_test = AuthTest()
    auth_test.test_password_hashing()
    auth_test.test_jwt_token()

    exception_test = ExceptionTest()
    exception_test.test_custom_exceptions()

    schema_test = SchemaTest()
    schema_test.test_response_schema()

    encryption_test = EncryptionTest()
    encryption_test.test_encryption()

    # 비동기 테스트 실행
    asyncio.run(run_async_tests())

    print("\n========== 공통 모듈 테스트 완료 ==========\n")


if __name__ == "__main__":
    run_tests()
