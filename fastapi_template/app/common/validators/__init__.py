"""
# File: fastapi_template/app/common/validators/__init__.py
# Description: 데이터 검증 모듈 초기화
"""

# 참고: 이 모듈에 데이터 검증 유틸리티 함수나 클래스를 추가하세요.
# 예: 이메일 검증, 비밀번호 정책 검사, 데이터 형식 검증 등

# 예시:
# def validate_email(email: str) -> bool:
#     # 이메일 유효성 검사 로직
#     return True

# 문자열 검증 유틸리티
from app.common.validators.string_validators import (
    validate_email,
    validate_password_strength,
    validate_phone_number,
)

# 데이터 검증 유틸리티
from app.common.validators.data_validators import (
    validate_required_fields,
    validate_numeric_range,
    validate_string_length,
    sanitize_input,
)

# 파일 검증 유틸리티
from app.common.validators.file_validators import (
    validate_file_extension,
    validate_file_size,
    validate_image_file,
    validate_mime_type,
)

__all__ = [
    # 문자열 검증
    "validate_email",
    "validate_password_strength",
    "validate_phone_number",
    # 데이터 검증
    "validate_required_fields",
    "validate_numeric_range",
    "validate_string_length",
    "sanitize_input",
    # 파일 검증
    "validate_file_extension",
    "validate_file_size",
    "validate_image_file",
    "validate_mime_type",
]
