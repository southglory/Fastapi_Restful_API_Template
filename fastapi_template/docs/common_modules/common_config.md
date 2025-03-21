# 설정 모듈 상세 가이드

이 문서는 FastAPI 템플릿의 설정 모듈에 대한 상세 사용법과 설명을 제공합니다.

## 목차

- [기본 설정](#기본-설정)
- [환경별 설정](#환경별-설정)
- [설정 확장](#설정-확장)
- [설정 유효성 검사](#설정-유효성-검사)

## 기본 설정

[@settings](/fastapi_template/app/common/config/settings.py)

애플리케이션 설정은 `app.common.config` 모듈을 통해 관리됩니다. 이 모듈은 환경 변수와 `.env` 파일로부터 설정값을 로드합니다.

### 설정 사용하기

```python
from app.common.config import settings

# 데이터베이스 설정
db_url = settings.DATABASE_URL
db_pool_size = settings.DB_POOL_SIZE

# API 설정
api_prefix = settings.API_PREFIX
debug_mode = settings.DEBUG

# 보안 설정
secret_key = settings.SECRET_KEY
token_expire = settings.ACCESS_TOKEN_EXPIRE_MINUTES
```

### 기본 설정 값

주요 설정 항목:

```python
# 애플리케이션 정보
APP_NAME = "FastAPI Template"
APP_VERSION = "0.1.0"
API_PREFIX = "/api"

# 개발 환경 설정
DEBUG = False
RELOAD = False

# 데이터베이스 설정
DATABASE_URL = "postgresql://postgres:postgres@localhost:5432/fastapi_db"
DB_POOL_SIZE = 5
DB_ECHO = False

# 인증 설정
SECRET_KEY = "your-secret-key"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# Redis 캐시 설정
REDIS_HOST = "localhost"
REDIS_PORT = 6379
REDIS_DB = 0
REDIS_PASSWORD = None
```

## 환경별 설정

[@environment](/fastapi_template/app/common/config/environment.py)

프로젝트는 여러 환경에 맞는 설정을 제공합니다.

### 개발 환경 설정

```python
from app.common.config import dev_settings

# 개발 환경 전용 설정
debug_mode = dev_settings.DEBUG  # True
database_url = dev_settings.DATABASE_URL  # "sqlite:///./dev.db"
```

### 테스트 환경 설정

```python
from app.common.config import test_settings

# 테스트 환경 전용 설정
database_url = test_settings.DATABASE_URL  # "sqlite:///./test.db"
```

### 프로덕션 환경 설정

```python
from app.common.config import prod_settings

# 프로덕션 환경 전용 설정
log_level = prod_settings.LOG_LEVEL  # "INFO"
```

## 설정 확장

[@base_settings](/fastapi_template/app/common/config/base_settings.py)

### 사용자 정의 설정 추가

프로젝트에 새로운 설정이 필요한 경우, `app/common/config/base_settings.py` 파일을 수정하고 필요한 설정을 추가할 수 있습니다.

```python
# 예: 이메일 서비스 설정 추가
class BaseSettings(BaseModel):
    # 기존 설정...
    
    # 새로운 이메일 설정
    EMAIL_HOST: str = "smtp.gmail.com"
    EMAIL_PORT: int = 587
    EMAIL_USERNAME: str = ""
    EMAIL_PASSWORD: str = ""
    EMAIL_USE_TLS: bool = True
```

### 설정 파일

프로젝트는 다음 설정 파일들을 사용합니다:

- `.env`: 기본 환경 설정
- `.env.dev`: 개발 환경 설정
- `.env.test`: 테스트 환경 설정
- `.env.prod`: 프로덕션 환경 설정

샘플 `.env` 파일:

```env
# 애플리케이션 설정
APP_NAME="FastAPI Template"
DEBUG=False

# 데이터베이스 설정
DATABASE_URL=postgresql://postgres:postgres@localhost:5432/fastapi_db

# 보안 설정
SECRET_KEY=your-secret-key
```

## 설정 유효성 검사

[@validators](/fastapi_template/app/common/config/validators.py)

모든 설정은 Pydantic 모델을 통해 타입 검증이 이루어집니다. 잘못된 설정 값이 제공되면 애플리케이션 시작 시 오류가 발생합니다.

### 설정 제약 조건

```python
class BaseSettings(BaseModel):
    # 기본 필드 및 제약 조건
    APP_NAME: str
    DEBUG: bool
    DATABASE_URL: PostgresDsn | str
    DB_POOL_SIZE: int = Field(ge=1, le=20)  # 1~20 사이의 값
    SECRET_KEY: str = Field(min_length=32)  # 최소 32자 이상
```

### 환경별 설정 적용

적절한 환경 파일을 선택하려면 `ENV` 환경 변수를 설정하세요:

```bash
# 개발 환경 실행
ENV=dev uvicorn app.main:app --reload

# 테스트 환경 실행
ENV=test pytest

# 프로덕션 환경 실행
ENV=prod uvicorn app.main:app
``` 