# Auth 모듈 테스트 가이드

[@auth](/fastapi_template/app/common/auth)

## 개요

`auth` 모듈은 애플리케이션의 인증 및 권한 부여 기능을 담당합니다. 이 모듈은 사용자 인증, 토큰 생성 및 검증, 권한 확인 등의 기능을 제공하며, 보안에 직접적인 영향을 미치기 때문에 철저한 테스트가 필요합니다.

## 모듈 구조 및 의존성

`auth` 모듈은 다음과 같은 구조로 구성되어 있습니다:

- **[@auth/jwt.py](/fastapi_template/app/common/auth/jwt.py)**: JWT 토큰 생성 및 검증 함수
- **[@auth/password.py](/fastapi_template/app/common/auth/password.py)**: 비밀번호 해싱 및 검증 함수
- **[@dependencies/auth.py](/fastapi_template/app/common/dependencies/auth.py)**: FastAPI 인증 의존성 함수

### Auth와 Dependencies 모듈 분리 원칙

1. **기능 분리**:
   - `auth` 모듈: 인증 관련 순수 로직을 구현한 유틸리티 함수 제공
   - `dependencies/auth`: FastAPI의 의존성 주입 시스템과 통합된 함수 제공

2. **의존성 방향**:
   - `dependencies/auth`는 `auth` 모듈에 의존
   - `auth` 모듈은 `dependencies`에 의존하지 않아야 함

3. **테스트 접근법**:
   - `auth` 모듈: 단위 테스트 중심 (순수 함수 테스트)
   - `dependencies/auth`: 통합 테스트 중심 (FastAPI 의존성 체인 테스트)

## 테스트 용이성

- **난이도**: 중간-어려움
- **이유**:
  - 인증 및 권한 부여 로직 테스트가 필요함
  - JWT 토큰 생성 및 검증 로직 테스트
  - 실제 사용자 인증 흐름을 시뮬레이션해야 함
  - 다양한 인증 상황(유효한 토큰, 만료된 토큰, 잘못된 토큰 등)에 대한 테스트 필요

## 테스트 대상

주요 테스트 대상은 다음과 같습니다:

1. **토큰 관련 기능** [@auth/jwt](/fastapi_template/app/common/auth/jwt.py)
   - JWT 토큰 생성
   - 토큰 검증
   - 만료 토큰 처리
   - 리프레시 토큰 기능

2. **인증 의존성 함수** [@dependencies/auth](/fastapi_template/app/common/dependencies/auth.py)
   - 현재 사용자 가져오기
   - 활성 사용자 확인
   - 관리자 권한 확인

3. **비밀번호 관련 기능** [@auth/password](/fastapi_template/app/common/auth/password.py)
   - 비밀번호 해싱
   - 비밀번호 검증
   - 비밀번호 강도 확인

## 테스트 접근법

Auth 모듈을 테스트할 때 다음 접근법을 권장합니다:

1. **모킹을 활용한 격리 테스트**: 데이터베이스, 외부 서비스 등의 의존성을 모킹하여 테스트합니다.
2. **다양한 시나리오 테스트**: 정상 케이스, 오류 케이스, 예외 케이스 등 다양한 상황을 테스트합니다.
3. **보안 취약점 테스트**: 잘못된 입력, 만료된 토큰, 권한 없는 접근 시도 등을 테스트합니다.

## 구현된 테스트 코드

각 인증 유형별 테스트 코드:

- [JWT 토큰 테스트 코드](/fastapi_template/tests/test_auth/test_jwt.py)
- [비밀번호 처리 테스트 코드](/fastapi_template/tests/test_auth/test_password.py)
- [인증 의존성 테스트 코드](/fastapi_template/tests/test_auth/test_deps.py)

## 테스트 예시

### JWT 토큰 테스트

```python
# tests/test_auth/test_jwt.py
import pytest
import jwt
from datetime import datetime, timedelta
from app.common.auth.jwt import create_access_token, verify_token

def test_create_access_token():
    # 테스트 데이터
    user_id = "user123"
    secret_key = "test_secret_key"
    expires_delta = timedelta(minutes=15)
    
    # 액세스 토큰 생성
    token = create_access_token(
        subject=user_id,
        expires_delta=expires_delta
    )
    
    # 토큰 검증
    assert isinstance(token, str)
    
    # 토큰 복호화하여 내용 확인
    payload = jwt.decode(token, secret_key, algorithms=["HS256"])
    assert payload["sub"] == user_id
    assert "exp" in payload

def test_verify_token():
    # 테스트용 토큰 생성
    user_id = "test_user"
    token = create_access_token(
        subject=user_id
    )
    
    # 토큰 검증 및 페이로드 확인
    payload = verify_token(token)
    
    # 페이로드 검증
    assert payload["sub"] == user_id
    assert "exp" in payload

def test_expired_token():
    # 만료된 토큰 생성
    user_id = "test_user"
    expires_delta = timedelta(seconds=-1)  # 이미 만료됨
    
    token = create_access_token(
        subject=user_id,
        expires_delta=expires_delta
    )
    
    # 만료된 토큰 검증 시 예외 발생
    with pytest.raises(Exception):
        verify_token(token)
```

### 비밀번호 처리 테스트

```python
# tests/test_auth/test_password.py
import pytest
from app.common.auth.password import get_password_hash, verify_password

def test_password_hashing():
    # 원본 비밀번호
    password = "안전한비밀번호123!"
    
    # 비밀번호 해싱
    hashed_password = get_password_hash(password)
    
    # 해시된 결과 검증
    assert password != hashed_password
    assert len(hashed_password) > 20  # 충분히 긴 해시 확인
    
    # 비밀번호 검증
    assert verify_password(password, hashed_password) == True
    assert verify_password("잘못된비밀번호", hashed_password) == False

@pytest.mark.parametrize("password,expected_valid,expected_message", [
    ("abc123", False, "비밀번호는 최소 8자 이상이어야 합니다"),
    ("password123", False, "비밀번호에 특수문자가 포함되어야 합니다"),
    ("Password!", False, "비밀번호에 숫자가 포함되어야 합니다"),
    ("Pass123!", True, None),
])
def test_password_strength(password, expected_valid, expected_message):
    from app.common.validators.password import validate_password_strength
    is_valid, message = validate_password_strength(password)
    assert is_valid == expected_valid
    if not expected_valid:
        assert message == expected_message
```

### 인증 의존성 테스트

```python
# tests/test_auth/test_deps.py
import pytest
from fastapi import HTTPException, Depends
from fastapi.security import OAuth2PasswordBearer
from unittest.mock import patch, MagicMock
import jwt
from datetime import datetime, timedelta
from app.common.dependencies.auth import get_current_user, get_current_active_user, get_current_admin_user

# 테스트용 사용자 데이터
test_user = {
    "id": 1,
    "username": "test_user",
    "email": "test@example.com",
    "is_active": True,
    "is_admin": False
}

test_admin = {
    "id": 2,
    "username": "admin_user",
    "email": "admin@example.com",
    "is_active": True,
    "is_admin": True
}

# 모의 데이터베이스 함수
async def mock_get_user_by_id(db, user_id):
    if user_id == 1:
        return test_user
    elif user_id == 2:
        return test_admin
    return None

@pytest.mark.asyncio
async def test_get_current_user():
    # 토큰 데이터
    secret_key = "test_secret_key"
    token_data = {"sub": "1"}  # 사용자 ID가 1
    
    # 유효한 토큰 생성
    token = jwt.encode(token_data, secret_key, algorithm="HS256")
    
    # 의존성 함수 테스트
    with patch("app.common.auth.verify_token") as mock_verify_token:
        mock_verify_token.return_value = token_data
        with patch("app.services.user_service.UserService.get_user") as mock_get_user:
            mock_get_user.side_effect = mock_get_user_by_id
            
            user = await get_current_user(token=token, db=MagicMock())
            assert user["id"] == 1
            assert user["username"] == "test_user"

@pytest.mark.asyncio
async def test_get_current_inactive_user():
    # 비활성 사용자 데이터
    inactive_user = {
        "id": 3,
        "username": "inactive_user",
        "email": "inactive@example.com",
        "is_active": False
    }
    
    # 의존성 함수 테스트
    with pytest.raises(HTTPException) as exc:
        await get_current_active_user(current_user=inactive_user)
    
    # 예외 검증
    assert exc.value.status_code == 400
    assert "Inactive user" in str(exc.value.detail)

@pytest.mark.asyncio
async def test_get_current_admin_user():
    # 일반 사용자로 관리자 권한 시도
    with pytest.raises(HTTPException) as exc:
        await get_current_admin_user(current_user=test_user)
    
    # 예외 검증
    assert exc.value.status_code == 403
    assert "Not enough privileges" in str(exc.value.detail)
    
    # 관리자 사용자로 시도
    admin = await get_current_admin_user(current_user=test_admin)
    assert admin["id"] == 2
    assert admin["is_admin"] == True
```

## 테스트 모킹 전략

Auth 모듈 테스트 시 다음과 같은 구성 요소를 모킹하는 것이 좋습니다:

1. **사용자 데이터베이스 액세스**: 실제 DB 연결 대신 모의 함수 사용
2. **토큰 생성/검증 함수**: 테스트용 키와 알고리즘 사용
3. **HTTP 요청/컨텍스트**: FastAPI의 TestClient 활용

## 테스트 커버리지 확인

Auth 모듈의 테스트 커버리지를 확인하세요:

```bash
pytest --cov=app.common.auth --cov=app.common.dependencies.auth tests/test_auth/ -v
```

## 보안 테스트 체크리스트

Auth 모듈 테스트를 위한 체크리스트:

- [ ] 유효한 사용자 인증 흐름 테스트
- [ ] 만료된 토큰 처리 테스트
- [ ] 잘못된 형식의 토큰 처리 테스트
- [ ] 권한 없는 접근 시도 테스트
- [ ] 비밀번호 해싱 및 검증 테스트
- [ ] 비밀번호 강도 검증 테스트
- [ ] 로그아웃 및 토큰 무효화 테스트
- [ ] 리프레시 토큰 갱신 테스트

## 모범 사례

1. 민감한 보안 기능은 여러 예외 상황을 철저히 테스트하세요.
2. 모의 객체를 사용하여 데이터베이스와 같은 외부 의존성을 격리하세요.
3. 시간에 의존하는 테스트(토큰 만료 등)는 고정된 시간을 사용하세요.
4. 보안 취약점을 발견할 수 있는 다양한 시나리오를 테스트하세요.

## 주의사항

1. 테스트에서 실제 비밀 키를 사용하지 마세요. 항상 테스트용 키를 사용하세요.
2. 테스트 환경에서 생성된 토큰이 실제 환경에서 사용되지 않도록 주의하세요.
3. 비밀번호 해싱 테스트는 실행 시간이 길어질 수 있으므로 테스트 효율성을 고려하세요.
