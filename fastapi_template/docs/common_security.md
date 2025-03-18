# 보안 모듈 상세 가이드

이 문서는 FastAPI 템플릿의 보안 모듈에 대한 상세 사용법과 설명을 제공합니다.

## 목차

- [암호화 유틸리티](#암호화-유틸리티)
- [CORS 설정](#cors-설정)
- [속도 제한](#속도-제한)
- [보안 헤더](#보안-헤더)

## 암호화 유틸리티

`app.common.security.encryption` 모듈은 데이터 암호화 및 복호화를 위한 유틸리티를 제공합니다.

### 기본 암호화/복호화

```python
from app.common.security.encryption import encrypt_data, decrypt_data

# 문자열 암호화
encrypted = encrypt_data("민감한 정보")

# 문자열 복호화
decrypted = decrypt_data(encrypted)
```

### Encryption 클래스 사용

```python
from app.common.security.encryption import Encryption

# 기본 키로 암호화 객체 생성
encryption = Encryption()

# 또는 사용자 지정 키 사용
encryption = Encryption(key="your-secret-key")

# 암호화
encrypted = encryption.encrypt("민감한 정보")

# 복호화
original = encryption.decrypt(encrypted)
```

### 객체 암호화

```python
from app.common.security.encryption import encrypt_object, decrypt_object

# 객체 암호화
user_data = {"id": 1, "ssn": "123-45-6789", "address": "서울시..."}
encrypted = encrypt_object(user_data)

# 객체 복호화
original = decrypt_object(encrypted)
```

## CORS 설정

### 기본 CORS 설정

```python
from fastapi import FastAPI
from app.common.security.cors import setup_cors

app = FastAPI()

# 기본 CORS 설정 적용
setup_cors(app)
```

### 사용자 정의 CORS 설정

```python
from fastapi import FastAPI
from app.common.security.cors import setup_cors

app = FastAPI()

# 사용자 정의 CORS 설정
setup_cors(
    app,
    allow_origins=["https://frontend.example.com"],
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["Authorization", "Content-Type"],
    allow_credentials=True,
    max_age=3600
)
```

## 속도 제한

API 요청 속도를 제한하여 서비스 남용을 방지합니다.

### 의존성으로 속도 제한 적용

```python
from fastapi import Depends
from app.common.security.rate_limit import rate_limiter

@app.get("/api/users", dependencies=[Depends(rate_limiter(limit=10, period=60))])
async def get_users():
    """분당 최대 10회 요청 가능"""
    return {"users": [...]}
```

### 데코레이터로 속도 제한 적용

```python
from app.common.security.rate_limit import RateLimit

# 클래스 데코레이터로 속도 제한 적용
@RateLimit(limit=5, period=60)  # 1분당 5회 제한
@app.post("/api/items")
async def create_item(item: Item):
    return {"item_id": 123}
```

### IP 기반 속도 제한

```python
from fastapi import Depends
from app.common.security.rate_limit import ip_rate_limiter

@app.post("/api/login", dependencies=[Depends(ip_rate_limiter(limit=5, period=300))])
async def login(credentials: LoginCredentials):
    """동일 IP에서 5분에 최대 5번만 로그인 시도 가능"""
    return await auth_service.login(credentials)
```

## 보안 헤더

보안 관련 HTTP 헤더를 설정하여 일반적인 웹 취약점을 방지합니다.

### 기본 보안 헤더 설정

```python
from fastapi import FastAPI
from app.common.security.headers import setup_security_headers

app = FastAPI()

# 기본 보안 헤더 설정
setup_security_headers(app)
```

### 보안 헤더 상세 설정

```python
from fastapi import FastAPI
from app.common.security.headers import setup_security_headers

app = FastAPI()

# 사용자 정의 보안 헤더 설정
setup_security_headers(
    app,
    content_security_policy="default-src 'self'; img-src 'self' https://cdn.example.com;",
    hsts_max_age=31536000,  # 1년
    include_subdomains=True,
    xframe_options="DENY"
)
```

### 주요 보안 헤더

설정되는 주요 보안 헤더:

- **Content-Security-Policy**: 콘텐츠 로드 출처 제한
- **X-XSS-Protection**: XSS 공격 방지
- **X-Content-Type-Options**: MIME 타입 스니핑 방지
- **Strict-Transport-Security**: HTTPS 강제
- **X-Frame-Options**: 클릭재킹 방지
- **Referrer-Policy**: 리퍼러 정보 제한 