# Config 모듈 상세 가이드

[@config](/fastapi_template/app/common/config)

## 개요

`config` 모듈은 애플리케이션의 설정을 관리하는 모듈입니다. 환경 변수, 설정 파일, 기본값 등을 관리하며, 애플리케이션의 다양한 설정을 중앙화된 방식으로 제공합니다.

## 현재 모듈 구조

```
app/common/config/
├── __init__.py                 # 모듈 초기화 및 내보내기
├── config_base.py              # 기본 설정 클래스
├── config_app.py               # 애플리케이션 설정
├── config_db.py                # 데이터베이스 설정
└── config_security.py          # 보안 설정
```

## 주요 기능

### 1. 기본 설정 (`config_base.py`)

- 기본 설정 클래스
- 환경 변수 로드
- 기본값 처리

### 2. 애플리케이션 설정 (`config_app.py`)

- 앱 이름/버전
- 디버그 모드
- 로깅 설정

### 3. 데이터베이스 설정 (`config_db.py`)

- DB URL
- 연결 풀
- 타임아웃

### 4. 보안 설정 (`config_security.py`)

- JWT 설정
- 암호화 키
- CORS 설정

## 사용 예시

### 기본 설정 사용

```python
from app.common.config import settings

# 애플리케이션 설정
app_name = settings.APP_NAME
debug_mode = settings.DEBUG

# 데이터베이스 설정
db_url = settings.DATABASE_URL
db_pool_size = settings.DB_POOL_SIZE

# 보안 설정
secret_key = settings.SECRET_KEY
token_expire = settings.ACCESS_TOKEN_EXPIRE_MINUTES
```

### 환경 변수 설정

```python
# .env 파일
APP_NAME="FastAPI Template"
DEBUG=False
DATABASE_URL="postgresql://user:password@localhost:5432/dbname"
SECRET_KEY="your-secret-key"
```

### 설정 유효성 검사

```python
from app.common.config import BaseSettings

class CustomSettings(BaseSettings):
    # 필수 설정
    APP_NAME: str
    DATABASE_URL: str
    
    # 선택적 설정 (기본값 포함)
    DEBUG: bool = False
    DB_POOL_SIZE: int = 5
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
```

## 모범 사례

1. 모든 설정 값의 기본값을 제공합니다.
2. 환경 변수를 적절히 처리합니다.
3. 설정 유효성 검사를 수행합니다.
4. 설정 변경 시 동작을 확인합니다.

## 주의사항

1. 실제 환경 변수를 테스트에 영향을 주지 않습니다.
2. 민감한 설정 값은 테스트용 더미 데이터를 사용합니다.
3. 설정 파일의 경로를 올바르게 처리합니다.
4. 설정 변경의 부작용을 고려합니다.

## 심화 가이드

설정 모듈에 대한 더 자세한 가이드는 다음 문서를 참조하세요:

1. [기본 설정](./config/01-base-settings.md) - 기본 설정 클래스
2. [애플리케이션 설정](./config/02-app-settings.md) - 앱 관련 설정
3. [데이터베이스 설정](./config/03-db-settings.md) - DB 관련 설정
4. [보안 설정](./config/04-security-settings.md) - 보안 관련 설정
