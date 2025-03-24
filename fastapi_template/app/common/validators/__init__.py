"""
# File: fastapi_template/app/common/validators/__init__.py
# Description: 데이터 검증 모듈 초기화
"""

# 참고: 이 모듈은 Pydantic 대신 순수 Python 함수로 유효성 검사 로직을 구현하였습니다.
# 그 이유는 다음과 같습니다:
# 1. 모듈 간 의존성 최소화: Pydantic에 의존하지 않고 순수 Python으로 구현하여 의존성 감소
# 2. 재사용성: 다양한 컨텍스트(API 요청, 파일 처리, 데이터베이스 등)에서 재사용 가능
# 3. 유연성: Pydantic 모델이 아닌 일반 데이터 구조(dict, list 등)에도 쉽게 적용 가능
# 4. 성능: 단순한 검증 작업에는 Pydantic 오버헤드 없이 더 가벼운 방식으로 처리 가능
#
# Config 모듈과의 연결 방법:
# 1. Config 모듈에서 설정을 로드한 후, 이 validators 모듈의 함수를 사용하여 추가 검증 수행
# 2. Settings 클래스의 validator 메서드 내에서 이 모듈의 함수를 호출하여 보다 복잡한 검증 로직 구현
# 3. API 엔드포인트나 서비스 레이어에서 config 설정값과 함께 이 validators를 활용하여
#    사용자 입력이나 외부 데이터의 유효성을 검증

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
