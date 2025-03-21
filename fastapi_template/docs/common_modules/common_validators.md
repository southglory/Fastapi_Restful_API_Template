# 데이터 검증 유틸리티 (Validators)

FastAPI 템플릿에서 제공하는 데이터 검증 유틸리티들에 대한 사용법과 예시입니다.

## 목차

- [문자열 검증](#문자열-검증)
- [데이터 검증](#데이터-검증)
- [파일 검증](#파일-검증)

## 설치 및 사용

validator 모듈은 기본적으로 설치되어 있으며, 다음과 같이 임포트하여 사용할 수 있습니다:

```python
from app.common.validators import validate_email, validate_password_strength
```

파일 검증 유틸리티를 사용하기 위해서는 추가 라이브러리가 필요합니다:

```bash
pip install python-magic      # Linux/macOS
pip install python-magic-bin  # Windows
```

## 문자열 검증

[@string_validators](/fastapi_template/app/common/validators/string_validators.py)

### 이메일 검증

```python
from app.common.validators import validate_email

# 사용 예시
is_valid = validate_email("user@example.com")  # True
is_valid = validate_email("invalid-email")     # False
```

### 비밀번호 강도 검증

```python
from app.common.validators import validate_password_strength

# 기본 설정으로 검증
is_valid, error_msg = validate_password_strength("Password123!")  # (True, None)
is_valid, error_msg = validate_password_strength("weak")          # (False, "비밀번호는 최소 8자 이상이어야 합니다.")

# 사용자 지정 요구사항으로 검증
is_valid, error_msg = validate_password_strength(
    "simple123", 
    min_length=6,
    require_uppercase=False,
    require_special_chars=False
)  # (True, None)
```

### 전화번호 검증

```python
from app.common.validators import validate_phone_number

# 한국 전화번호 (기본값)
is_valid = validate_phone_number("01012345678")  # True

# 미국 전화번호
is_valid = validate_phone_number("1234567890", country_code="US")  # True
```

## 데이터 검증

[@data_validators](/fastapi_template/app/common/validators/data_validators.py)

### 필수 필드 검증

```python
from app.common.validators import validate_required_fields

data = {"name": "John", "email": "john@example.com", "age": None}
is_valid, error_msg = validate_required_fields(data, ["name", "email", "address"])
# (False, "다음 필드가 누락되었습니다: address")
```

### 숫자 범위 검증

```python
from app.common.validators import validate_numeric_range

# 범위 검증
is_valid, error_msg = validate_numeric_range(25, min_value=18, max_value=65)  # (True, None)
is_valid, error_msg = validate_numeric_range(15, min_value=18)  # (False, "값(15)이 최소값(18)보다 작습니다.")
```

### 문자열 길이 검증

```python
from app.common.validators import validate_string_length

# 길이 검증
is_valid, error_msg = validate_string_length("username", min_length=3, max_length=20)  # (True, None)
is_valid, error_msg = validate_string_length("a", min_length=3)  # (False, "문자열 길이(1)가 최소 길이(3)보다 짧습니다.")
```

### 입력 정제 (Sanitization)

```python
from app.common.validators import sanitize_input

# HTML 및 SQL 인젝션 방지
safe_text = sanitize_input("<script>alert('XSS');</script>")  # "alert('XSS');"
safe_query = sanitize_input("users'; DROP TABLE users;")      # "users DROP TABLE users"
```

## 파일 검증

[@file_validators](/fastapi_template/app/common/validators/file_validators.py)

### 파일 확장자 검증

```python
from app.common.validators import validate_file_extension

# 확장자 검증
allowed_exts = {".jpg", ".png", ".gif"}
is_valid, error_msg = validate_file_extension("image.jpg", allowed_exts)  # (True, None)
is_valid, error_msg = validate_file_extension("script.js", allowed_exts)
# (False, "파일 확장자 '.js'은(는) 허용되지 않습니다. 허용된 확장자: .jpg, .png, .gif")
```

### 파일 크기 검증

```python
from app.common.validators import validate_file_size

# 크기 검증 (5MB 제한)
max_size = 5 * 1024 * 1024  # 5MB in bytes
is_valid, error_msg = validate_file_size(2 * 1024 * 1024, max_size)  # (True, None) - 2MB 파일
is_valid, error_msg = validate_file_size(10 * 1024 * 1024, max_size)
# (False, "파일 크기(10.0 MB)가 최대 허용 크기(5.0 MB)를 초과합니다.")
```

### 이미지 파일 검증

```python
from app.common.validators import validate_image_file

# 이미지 파일 검증
is_valid, error_msg = validate_image_file("/path/to/image.jpg")  # (True, None)
is_valid, error_msg = validate_image_file("/path/to/text.txt")
# (False, "'.txt' 확장자는 허용된 이미지 형식이 아닙니다...")
```

### MIME 타입 검증

```python
from app.common.validators import validate_mime_type

# MIME 타입 검증
allowed_types = ["application/pdf", "text/plain"]
is_valid, error_msg = validate_mime_type("/path/to/document.pdf", allowed_types)  # (True, None)
is_valid, error_msg = validate_mime_type("/path/to/image.jpg", allowed_types)
# (False, "파일 타입(image/jpeg)은 허용되지 않습니다...")
```

## 커스텀 검증 함수 추가

프로젝트에 필요한 커스텀 검증 함수를 추가하려면 적절한 파일에 함수를 추가하고, `__init__.py`에 임포트하세요.

예시:

```python
# app/common/validators/string_validators.py에 함수 추가
def validate_url(url: str) -> bool:
    """URL이 유효한지 검증합니다."""
    url_pattern = r"^https?://[^\s/$.?#].[^\s]*$"
    return bool(re.match(url_pattern, url))

# app/common/validators/__init__.py에 임포트 추가
from app.common.validators.string_validators import validate_url
__all__ += ["validate_url"]
```
