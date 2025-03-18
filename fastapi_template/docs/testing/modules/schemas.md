# Schemas 모듈 테스트 가이드

## 개요

`schemas` 모듈은 API 요청 및 응답의 데이터 구조를 정의하고 검증하는 역할을 담당합니다. 이 모듈은 Pydantic 모델을 사용하여 데이터 유효성 검사, 타입 변환, 직렬화/역직렬화를 처리합니다. 이런 특성으로 인해 테스트는 대체로 단순하며 외부 의존성이 적습니다.

## 테스트 용이성

- **난이도**: 쉬움-중간
- **이유**:
  - Pydantic 모델 기반으로 검증 로직이 명확함
  - 단순한 데이터 구조 검증은 쉽게 테스트 가능
  - 복잡한 유효성 검증 규칙이 있는 경우 테스트가 복잡할 수 있음

## 테스트 대상

주요 테스트 대상은 다음과 같습니다:

1. **기본 스키마 검증**
   - 필수 필드 검증
   - 필드 타입 검증
   - 기본값 적용

2. **고급 검증 규칙**
   - 커스텀 검증기 (validators)
   - 필드 간 의존성 검증
   - 복잡한 비즈니스 규칙 검증

3. **스키마 변환**
   - 모델 간 변환 (예: DB 모델 → API 스키마)
   - 직렬화/역직렬화 (JSON 변환 등)
   - 데이터 정제 및 변환

## 테스트 접근법

Schemas 모듈 테스트 시 다음 접근법을 권장합니다:

1. **정상 케이스 테스트**: 유효한 데이터로 스키마 생성 및 검증
2. **예외 케이스 테스트**: 잘못된 데이터로 예외 발생 확인
3. **경계값 테스트**: 유효/무효의 경계에 있는 값 테스트
4. **변환 테스트**: 모델 간 변환 및 직렬화/역직렬화 테스트

## 테스트 예시

### 기본 스키마 검증 테스트

```python
# tests/test_schemas/test_base_schema.py
import pytest
from pydantic import ValidationError
from app.common.schemas.base_schema import ResponseSchema

def test_response_schema_valid_data():
    # 유효한 데이터로 스키마 인스턴스 생성
    response = ResponseSchema(
        success=True,
        message="Operation successful",
        data={"user_id": 123, "username": "testuser"}
    )
    
    # 필드 값 검증
    assert response.success is True
    assert response.message == "Operation successful"
    assert response.data["user_id"] == 123
    assert response.data["username"] == "testuser"

def test_response_schema_invalid_data():
    # 잘못된 데이터로 예외 발생 확인
    with pytest.raises(ValidationError) as exc:
        ResponseSchema(
            success="not_a_boolean",  # bool 타입이어야 함
            message=123,  # str 타입이어야 함
            data="not_a_dict"  # dict 타입이어야 함
        )
    
    # 예외 내용 검증
    errors = exc.value.errors()
    assert any("success" in e["loc"] for e in errors)
    assert any("message" in e["loc"] for e in errors)
    assert any("data" in e["loc"] for e in errors)

def test_response_schema_default_values():
    # 일부 필드만 제공하고 나머지는 기본값 적용
    response = ResponseSchema(data={"test": "value"})
    
    # 기본값 검증
    assert response.success is True  # 기본값 True
    assert response.message == "Success"  # 기본값 "Success"
    assert response.data == {"test": "value"}
```

### 사용자 스키마 테스트

```python
# tests/test_schemas/test_user_schema.py
import pytest
from pydantic import ValidationError
from datetime import datetime
from app.db.schemas.user import UserCreate, UserResponse, UserUpdate

def test_user_create_valid():
    # 유효한 사용자 생성 스키마
    user_data = {
        "username": "testuser",
        "email": "test@example.com",
        "password": "Password123!"
    }
    user = UserCreate(**user_data)
    
    # 값 검증
    assert user.username == "testuser"
    assert user.email == "test@example.com"
    assert user.password == "Password123!"

def test_user_create_invalid_email():
    # 잘못된 이메일 형식
    with pytest.raises(ValidationError) as exc:
        UserCreate(
            username="testuser",
            email="invalid-email",  # 올바른 이메일 형식이 아님
            password="Password123!"
        )
    
    # 예외 내용 검증
    errors = exc.value.errors()
    assert any("email" in e["loc"] for e in errors)

def test_user_create_password_validation():
    # 비밀번호 복잡성 규칙 검증
    # 너무 짧은 비밀번호
    with pytest.raises(ValidationError) as exc:
        UserCreate(
            username="testuser",
            email="test@example.com",
            password="short"  # 비밀번호가 너무 짧음
        )
    
    # 숫자가 없는 비밀번호
    with pytest.raises(ValidationError) as exc:
        UserCreate(
            username="testuser",
            email="test@example.com",
            password="Password!"  # 숫자 없음
        )
    
    # 대문자가 없는 비밀번호
    with pytest.raises(ValidationError) as exc:
        UserCreate(
            username="testuser",
            email="test@example.com",
            password="password123!"  # 대문자 없음
        )

def test_user_response_model():
    # 사용자 응답 스키마 테스트
    created_at = datetime.now()
    user_data = {
        "id": 1,
        "username": "testuser",
        "email": "test@example.com",
        "is_active": True,
        "created_at": created_at
    }
    user = UserResponse(**user_data)
    
    # 값 검증
    assert user.id == 1
    assert user.username == "testuser"
    assert user.email == "test@example.com"
    assert user.is_active is True
    assert user.created_at == created_at
    
    # 비밀번호 필드가 없는지 확인 (응답에 포함되면 안 됨)
    assert not hasattr(user, "password")
    assert not hasattr(user, "hashed_password")

def test_user_update_partial():
    # 부분 업데이트 테스트
    # 일부 필드만 제공
    user_update = UserUpdate(username="new_username")
    
    # 제공된 필드만 있고 나머지는 None
    assert user_update.username == "new_username"
    assert user_update.email is None
    assert user_update.password is None
```

### 스키마 변환 테스트

```python
# tests/test_schemas/test_schema_conversion.py
from datetime import datetime
from app.db.models.user import User
from app.db.schemas.user import UserResponse
from app.common.schemas.base_schema import convert_model_to_schema

def test_convert_model_to_schema():
    # DB 모델 인스턴스 생성
    user_model = User(
        id=1,
        username="testuser",
        email="test@example.com",
        hashed_password="hashed_secret",
        is_active=True,
        created_at=datetime(2023, 1, 1, 12, 0, 0)
    )
    
    # DB 모델을 API 스키마로 변환
    user_schema = convert_model_to_schema(user_model, UserResponse)
    
    # 변환 결과 검증
    assert user_schema.id == 1
    assert user_schema.username == "testuser"
    assert user_schema.email == "test@example.com"
    assert user_schema.is_active is True
    assert user_schema.created_at == datetime(2023, 1, 1, 12, 0, 0)
    
    # 민감한 필드가 제외되었는지 확인
    assert not hasattr(user_schema, "hashed_password")

def test_response_schema_json():
    # 응답 스키마 JSON 직렬화 테스트
    response = ResponseSchema(
        success=True,
        message="Success",
        data={"id": 1, "name": "Test"}
    )
    
    # JSON 변환
    json_data = response.json()
    
    # JSON 형식 검증
    assert '"success": true' in json_data
    assert '"message": "Success"' in json_data
    assert '"id": 1' in json_data
    assert '"name": "Test"' in json_data
```

### 중첩 스키마 테스트

```python
# tests/test_schemas/test_nested_schemas.py
import pytest
from pydantic import ValidationError
from app.db.schemas.item import ItemResponse
from app.db.schemas.user import UserResponse

def test_nested_schema():
    # 사용자 정보를 포함한 아이템 응답 스키마 테스트
    item_data = {
        "id": 1,
        "title": "Test Item",
        "description": "This is a test item",
        "owner": {
            "id": 2,
            "username": "itemowner",
            "email": "owner@example.com",
            "is_active": True,
            "created_at": "2023-01-02T12:00:00"
        }
    }
    
    # 중첩 스키마 생성
    item = ItemResponse(**item_data)
    
    # 아이템 필드 검증
    assert item.id == 1
    assert item.title == "Test Item"
    assert item.description == "This is a test item"
    
    # 중첩된 소유자 객체 검증
    assert item.owner.id == 2
    assert item.owner.username == "itemowner"
    assert item.owner.email == "owner@example.com"
    assert item.owner.is_active is True
    
    # 중첩 객체의 타입 검증
    assert isinstance(item.owner, UserResponse)

def test_nested_schema_invalid():
    # 잘못된 중첩 데이터 테스트
    item_data = {
        "id": 1,
        "title": "Test Item",
        "description": "This is a test item",
        "owner": {
            "id": 2,
            "username": "itemowner",
            # 필수 필드 email 누락
            "is_active": True,
            "created_at": "2023-01-02T12:00:00"
        }
    }
    
    # 중첩 객체의 필수 필드 누락으로 인한 예외 발생 확인
    with pytest.raises(ValidationError) as exc:
        ItemResponse(**item_data)
    
    # 예외 내용 검증
    errors = exc.value.errors()
    assert any("email" in str(e) for e in errors)
```

## 테스트 커버리지 확인

Schemas 모듈의 테스트 커버리지를 확인하세요:

```bash
pytest --cov=app.common.schemas tests/test_schemas/
```

## 모범 사례

1. **다양한 입력 케이스 테스트**: 유효한 값, 무효한 값, 경계값, 특수 케이스 등을 테스트하세요.
2. **모든 검증 규칙 테스트**: 커스텀 유효성 검증 로직을 포함한 모든 규칙을 테스트하세요.
3. **변환 정확성 검증**: 모델 간 변환이 정확하게 이루어지는지 확인하세요.
4. **스키마의 목적에 맞는 테스트**: 응답 스키마와 요청 스키마의 목적에 맞게 별도로 테스트하세요.

## 주의사항

1. **복잡한 유효성 검증 로직**: 커스텀 유효성 검증기는 독립적으로 테스트하는 것이 좋습니다.
2. **순환 의존성**: 순환 참조가 있는 중첩 스키마는 테스트 시 주의가 필요합니다.
3. **스키마 간 일관성**: API 버전 간 스키마 변경 시 하위 호환성을 테스트하세요.
4. **실제 검증 로직의 위치**: 스키마의 유효성 검증 로직이 복잡한 경우, 해당 로직을 별도의 함수로 분리하고 그 함수를 직접 테스트하는 것이 더 효율적일 수 있습니다.
