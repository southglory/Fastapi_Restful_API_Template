"""
# File: fastapi_template/app/common/validators/string_validators.py
# Description: 문자열 검증 유틸리티 함수
"""

import re
from typing import Optional


def validate_email(email: str) -> bool:
    """
    이메일 주소가 유효한 형식인지 검증합니다.

    Args:
        email: 검증할 이메일 주소

    Returns:
        bool: 이메일이 유효하면 True, 아니면 False
    """
    email_pattern = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
    return bool(re.match(email_pattern, email))


def validate_password_strength(
    password: str,
    min_length: int = 8,
    require_uppercase: bool = True,
    require_lowercase: bool = True,
    require_digits: bool = True,
    require_special_chars: bool = True,
) -> tuple[bool, Optional[str]]:
    """
    비밀번호 강도를 검증합니다.

    Args:
        password: 검증할 비밀번호
        min_length: 최소 길이
        require_uppercase: 대문자 포함 여부
        require_lowercase: 소문자 포함 여부
        require_digits: 숫자 포함 여부
        require_special_chars: 특수문자 포함 여부

    Returns:
        tuple[bool, Optional[str]]: (검증 결과, 실패 시 오류 메시지)
    """
    if len(password) < min_length:
        return False, f"비밀번호는 최소 {min_length}자 이상이어야 합니다."

    if require_uppercase and not any(c.isupper() for c in password):
        return False, "비밀번호에는 최소 하나의 대문자가 포함되어야 합니다."

    if require_lowercase and not any(c.islower() for c in password):
        return False, "비밀번호에는 최소 하나의 소문자가 포함되어야 합니다."

    if require_digits and not any(c.isdigit() for c in password):
        return False, "비밀번호에는 최소 하나의 숫자가 포함되어야 합니다."

    if require_special_chars and not any(not c.isalnum() for c in password):
        return False, "비밀번호에는 최소 하나의 특수문자가 포함되어야 합니다."

    return True, None


def validate_phone_number(phone: str, country_code: str = "KR") -> bool:
    """
    전화번호가 유효한 형식인지 검증합니다.

    Args:
        phone: 검증할 전화번호
        country_code: 국가 코드 (ISO 3166-1 alpha-2)

    Returns:
        bool: 전화번호가 유효하면 True, 아니면 False
    """
    # 국가별 전화번호 패턴 정의
    patterns = {
        "KR": r"^01[0-1|6-9][0-9]{7,8}$",  # 한국 휴대폰 번호 (하이픈 없음)
        "US": r"^\d{3}[-.]?\d{3}[-.]?\d{4}$",  # 미국 전화번호
        # 필요에 따라 다른 국가 패턴 추가
    }

    pattern = patterns.get(country_code)
    if not pattern:
        raise ValueError(f"지원되지 않는 국가 코드: {country_code}")

    return bool(re.match(pattern, phone))
