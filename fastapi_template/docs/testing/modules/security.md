# Security 모듈 테스트 가이드

## 개요

`security` 모듈은 애플리케이션의 보안 관련 기능을 담당합니다. 주로 암호화, 해싱, 키 관리 등의 기능을 제공하며, 다른 보안 관련 모듈(예: auth)의 기반이 됩니다.

## 테스트 용이성

- **난이도**: 쉬움-중간
- **이유**:
  - 대부분 순수 함수이나 일부 외부 라이브러리에 의존
  - 암호화/복호화 기능은 결정적이며 테스트하기 쉬움
  - 키 생성 등 일부 기능은 랜덤성을 포함해 테스트가 복잡할 수 있음

## 테스트 대상

주요 테스트 대상은 다음과 같습니다:

1. **암호화/복호화 기능**
   - 대칭 암호화 (AES 등)
   - 비대칭 암호화 (RSA 등)
   - 암호화 키 관리

2. **해싱 기능**
   - 단방향 해시 함수
   - Salt 사용한 해싱
   - 해시 검증

3. **보안 유틸리티**
   - 안전한 난수 생성
   - 보안 토큰 생성
   - 서명 생성 및 검증

## 테스트 접근법

Security 모듈 테스트 시 다음 접근법을 권장합니다:

1. **단방향 테스트**: 해시 함수는 입력에 대한 출력만 검증합니다.
2. **양방향 테스트**: 암호화/복호화 함수는 원본 데이터 복원이 정확한지 검증합니다.
3. **랜덤 요소 제어**: 테스트에서 랜덤성이 요구되는 부분은 모의 함수를 사용하여 고정된 값을 반환하도록 합니다.

## 테스트 예시

### 암호화/복호화 테스트

```python
# tests/test_security/test_encryption.py
import pytest
from app.common.security.encryption import Encryption

def test_encryption():
    # 암호화 객체 생성
    encryption = Encryption(key="test_secret_key_for_test")
    
    # 텍스트 암호화 및 복호화 테스트
    original_text = "민감한 정보"
    encrypted = encryption.encrypt(original_text)
    decrypted = encryption.decrypt(encrypted)
    
    # 검증
    assert original_text != encrypted  # 암호화된 텍스트는 원본과 달라야 함
    assert original_text == decrypted  # 복호화된 텍스트는 원본과 같아야 함

def test_encryption_with_different_keys():
    # 서로 다른 키로 암호화/복호화 시도
    encryption1 = Encryption(key="key1")
    encryption2 = Encryption(key="key2")
    
    text = "테스트 메시지"
    encrypted = encryption1.encrypt(text)
    
    # 다른 키로 복호화 시도 시 예외 발생 확인
    with pytest.raises(Exception):
        decrypted = encryption2.decrypt(encrypted)
```

### 해싱 테스트

```python
# tests/test_security/test_hashing.py
import pytest
from app.common.security.hashing import hash_password, verify_hash

def test_hash_password():
    # 패스워드 해싱
    password = "my_secret_password"
    hashed = hash_password(password)
    
    # 같은 패스워드로 다시 해싱하면 다른 결과 (salt 사용)
    hashed2 = hash_password(password)
    assert hashed != hashed2
    
    # 해시 검증
    assert verify_hash(password, hashed) == True
    assert verify_hash("wrong_password", hashed) == False

@pytest.mark.parametrize("password", [
    "simple",
    "complex_password123!",
    "한글패스워드123",
    "!@#$%^&*()",
    ""  # 빈 문자열 테스트
])
def test_hash_various_inputs(password):
    hashed = hash_password(password)
    assert verify_hash(password, hashed) == True
```

### 보안 토큰 생성 테스트

```python
# tests/test_security/test_token.py
from unittest.mock import patch
from app.common.security.token import generate_secure_token, validate_token

def test_generate_secure_token():
    # 토큰 생성
    token = generate_secure_token(length=32)
    
    # 검증
    assert len(token) == 32
    assert isinstance(token, str)
    
    # 다른 토큰 생성
    another_token = generate_secure_token(length=32)
    assert token != another_token  # 랜덤성 확인

# 랜덤성 제어를 위한 모의 함수 테스트
def test_generate_token_with_mock():
    with patch('app.common.security.token.secrets.token_hex') as mock_token:
        mock_token.return_value = 'abcdef1234567890'
        token = generate_secure_token(length=8)
        assert token == 'abcdef12'  # 길이가 8인 토큰
        mock_token.assert_called_once_with(8)
```

## 모킹 전략

Security 모듈 테스트 시 다음과 같은 부분에 모킹을 적용하는 것이 좋습니다:

1. **랜덤 함수**: `random`, `secrets` 모듈의 함수들
2. **시간 관련 함수**: 토큰 만료 시간 테스트를 위한 `time.time()` 등
3. **외부 라이브러리 호출**: 암호화 라이브러리의 일부 기능

## 테스트 커버리지 확인

Security 모듈은 보안 중요성을 고려하여 높은 테스트 커버리지를 유지해야 합니다:

```bash
pytest --cov=app.common.security tests/test_security/
```

## 모범 사례

1. 다양한 입력값에 대한 테스트를 작성하세요 (정상, 경계, 오류 케이스).
2. 랜덤성이 있는 함수는 모의 함수를 사용하여 결정적으로 만들어 테스트하세요.
3. 암호화 키와 같은 민감한 정보는 테스트용 값을 사용하고, 실제 값을 코드에 포함하지 마세요.
4. 해싱 함수의 경우 다양한 길이와 문자 종류를 포함한 입력으로 테스트하세요.

## 주의사항

1. 실제 키나 비밀정보를 테스트 코드에 하드코딩하지 마세요.
2. 암호화 알고리즘의 보안성을 테스트하는 것이 아니라, 구현의 정확성을 테스트하는 것에 집중하세요.
3. 랜덤성이 있는 함수 테스트 시, 출력값을 정확히 예측하기보다 출력의 특성(길이, 형식 등)을 검증하세요.
4. 성능에 민감한 해싱 함수의 경우, 테스트 실행 시간을 고려하여 반복 횟수를 적절히 조절하세요.
