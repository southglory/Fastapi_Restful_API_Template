# 마이그레이션 설정

이 문서는 FastAPI 프로젝트에서 Alembic을 사용한 데이터베이스 마이그레이션 설정 방법을 설명합니다.

## 목차

1. [Alembic 소개](#alembic-소개)
2. [Alembic 설치](#alembic-설치)
3. [초기 설정](#초기-설정)
4. [마이그레이션 파일 생성](#마이그레이션-파일-생성)
5. [마이그레이션 적용](#마이그레이션-적용)
6. [마이그레이션 롤백](#마이그레이션-롤백)
7. [개발 환경 설정](#개발-환경-설정)
8. [문제 해결](#일반적인-문제-해결)

## Alembic 소개

Alembic은 SQLAlchemy를 위한 데이터베이스 마이그레이션 도구입니다. 데이터베이스 스키마 변경 사항을 버전 관리하고 적용할 수 있습니다.

주요 기능:

- 데이터베이스 스키마 변경 이력 관리
- 자동 마이그레이션 스크립트 생성
- 마이그레이션 적용 및 롤백

## Alembic 설치

Alembic은 이미 프로젝트 의존성에 포함되어 있습니다. 별도 설치가 필요하지 않습니다.

새 프로젝트에서는 다음과 같이 설치할 수 있습니다:

```bash
pip install alembic
```

프로젝트의 `requirements.txt`에 추가하는 것이 좋습니다:

```
# requirements.txt
alembic
```

## 초기 설정

### 1. Alembic 초기화

프로젝트에 이미 Alembic이 설정되어 있습니다. 새로운 프로젝트에서는 다음 명령으로 초기화할 수 있습니다:

```bash
alembic init alembic
```

이 명령은 다음과 같은 파일 구조를 생성합니다:

```
fastapi_template/
├── alembic/
│   ├── versions/
│   │   └── (마이그레이션 파일들)
│   ├── env.py
│   ├── README
│   └── script.py.mako
└── alembic.ini
```

### 2. 데이터베이스 URL 설정

`alembic.ini` 파일에서 데이터베이스 URL을 직접 설정하지 않고, 환경 변수에서 가져오도록 설정합니다:

```ini
# alembic.ini
[alembic]
# ...
# sqlalchemy.url = driver://user:pass@localhost/dbname
```

`env.py`에서 URL을 설정합니다:

```python
# DB URL을 환경 변수에서 가져오기
from app.common.config import settings
config.set_main_option("sqlalchemy.url", settings.DATABASE_URL)
```

### 3. Alembic 환경 설정

`alembic/env.py` 파일을 수정하여 SQLAlchemy 모델을 인식하도록 설정합니다:

```python
# alembic/env.py
from logging.config import fileConfig

from sqlalchemy import engine_from_config, pool

from alembic import context

import os
import sys
from pathlib import Path

# 프로젝트 루트 디렉토리를 Python 경로에 추가
sys.path.append(str(Path(__file__).parent.parent))

# Alembic Config 객체
config = context.config

# DB URL을 환경 변수에서 가져오기
# 개발 환경에서는 dev_settings 사용
from app.common.config import dev_settings

config.set_main_option("sqlalchemy.url", dev_settings.DATABASE_URL)

# 로깅 설정
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# 모델 가져오기
from app.common.database.base import Base
from app.db.models.user import User
from app.db.models.item import Item

# MetaData 객체 설정
target_metadata = Base.metadata

# ... 나머지 코드 ...
```

### 4. 마이그레이션 감지 옵션 설정

`env.py` 파일의 `run_migrations_online` 함수에서 다음과 같은 중요한 옵션을 설정합니다:

```python
def run_migrations_online() -> None:
    # ...
    with connectable.connect() as connection:
        context.configure(
            connection=connection, 
            target_metadata=target_metadata,
            compare_type=True,  # 컬럼 타입 변경 감지
            compare_server_default=True  # 기본값 변경 감지
        )
    # ...
```

이 옵션들의 역할:

- **compare_type=True**: 컬럼 데이터 타입 변경을 감지합니다. 예를 들어 `String(50)`에서 `String(100)`으로 변경된 경우를 감지합니다.
- **compare_server_default=True**: 컬럼의 기본값(DEFAULT) 변경을 감지합니다. 예를 들어 `default=0`에서 `default=1`로 변경된 경우를 감지합니다.

이 옵션들을 활성화하면 더 정확한 마이그레이션 스크립트가 생성됩니다.

### 5. 인코딩 설정

`alembic.ini` 파일에서 출력 인코딩을 UTF-8로 설정합니다:

```ini
# alembic.ini
[alembic]
# ...
# the output encoding used when revision files
# are written from script.py.mako
output_encoding = utf-8
```

## 마이그레이션 파일 생성

### 자동 마이그레이션 파일 생성

모델 변경 사항을 감지하여 자동으로 마이그레이션 파일을 생성합니다:

**중요**: Windows 환경에서는 인코딩 문제를 피하기 위해 `alembic.ini` 파일과 마이그레이션 메시지에 한글을 사용하지 마세요. 영어로 작성하는 것이 가장 간단한 해결책입니다.

```bash
# 영어로 마이그레이션 메시지 작성
alembic revision --autogenerate -m "initial"
```

예시:

```bash
alembic revision --autogenerate -m "Create user and item tables"
```

이 명령은 `alembic/versions/` 디렉토리에 새로운 마이그레이션 파일을 생성합니다.

### 수동 마이그레이션 파일 생성

특정 변경 사항을 수동으로 작성할 수도 있습니다:

```bash
alembic revision -m "설명"
```

그런 다음 생성된 파일에서 `upgrade()` 및 `downgrade()` 함수를 직접 작성합니다.

## 마이그레이션 적용

### 최신 버전으로 마이그레이션

모든 마이그레이션을 최신 버전으로 적용합니다:

```bash
alembic upgrade head
```

### 특정 버전으로 마이그레이션

특정 버전까지 마이그레이션을 적용합니다:

```bash
alembic upgrade 1a2b3c4d5e6f
```

### 상대적 마이그레이션

현재 버전에서 상대적으로 마이그레이션을 적용합니다:

```bash
alembic upgrade +1  # 한 단계 앞으로
```

## 마이그레이션 롤백

### 이전 버전으로 롤백

마이그레이션을 이전 버전으로 롤백합니다:

```bash
alembic downgrade -1  # 한 단계 뒤로
```

### 특정 버전으로 롤백

특정 버전으로 롤백합니다:

```bash
alembic downgrade 1a2b3c4d5e6f
```

### 초기 상태로 롤백

모든 마이그레이션을 롤백하여 초기 상태로 되돌립니다:

```bash
alembic downgrade base
```

## 개발 환경 설정

### SQLite 사용하기

개발 환경에서는 PostgreSQL 대신 SQLite를 사용하여 간편하게 개발할 수 있습니다. 이를 위해 별도의 환경 설정 파일(`.env.dev`)을 사용합니다.

1. **개발용 환경 설정 파일 생성**:

```
# .env.dev
DATABASE_URL=sqlite:///./dev.db
DB_ECHO_LOG=True
SECRET_KEY=dev-secret-key-for-testing
DEBUG=True
```

2. **config.py에 개발 환경 설정 추가**:

```python
# app/common/config.py

# 기본 설정 클래스
class Settings(BaseSettings):
    # ... 기존 설정 ...
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True
    )

# 기본 설정 인스턴스
settings = Settings()

# 개발 환경 설정 클래스
class DevSettings(Settings):
    DEBUG: bool = True
    DATABASE_URL: str = "sqlite:///./dev.db"
    
    model_config = SettingsConfigDict(
        env_file=".env.dev",
        env_file_encoding="utf-8",
        case_sensitive=True
    )

# 개발 환경 설정 인스턴스
dev_settings = DevSettings()
```

3. **env.py에서 개발 환경 설정 사용**:

```python
# alembic/env.py

# DB URL을 환경 변수에서 가져오기
# 개발 환경에서는 dev_settings 사용
from app.common.config import dev_settings

config.set_main_option("sqlalchemy.url", dev_settings.DATABASE_URL)
```

이렇게 설정하면 개발 환경에서는 SQLite를 사용하고, 프로덕션 환경에서는 PostgreSQL을 사용할 수 있습니다.

## 마이그레이션 이력 확인

현재 적용된 마이그레이션 이력을 확인합니다:

```bash
alembic history
alembic current  # 현재 버전 확인
```

## 일반적인 문제 해결

### 모듈을 찾을 수 없음

Alembic이 애플리케이션 모듈을 찾지 못하는 경우:

```
ModuleNotFoundError: No module named 'app'
```

해결 방법:

1. `PYTHONPATH` 환경 변수 설정: `export PYTHONPATH=$PYTHONPATH:$(pwd)`
2. `env.py`에 Python 경로 추가 (위에서 설명한 대로)

### 데이터베이스 연결 오류

데이터베이스 연결에 실패하는 경우:

```
sqlalchemy.exc.OperationalError: (psycopg2.OperationalError) could not connect to server
```

해결 방법:

1. 데이터베이스 서버가 실행 중인지 확인
2. 데이터베이스 URL이 올바른지 확인
3. 데이터베이스 사용자 권한 확인
4. 개발 환경에서는 SQLite로 전환 (위에서 설명한 대로)

### 인코딩 문제

Windows 환경에서 인코딩 문제가 발생하는 경우, 가장 간단한 해결책은 한글 대신 영어를 사용하는 것입니다:

```bash
# 영어로 마이그레이션 메시지 작성
alembic revision --autogenerate -m "initial"
```

## 마이그레이션 관리 팁

1. **마이그레이션 파일 검토**: 자동 생성된 마이그레이션 파일을 항상 검토하여 의도한 변경사항이 정확히 반영되었는지 확인하세요.

2. **테스트 환경에서 먼저 적용**: 프로덕션 환경에 적용하기 전에 테스트 환경에서 마이그레이션을 테스트하세요.

3. **마이그레이션 히스토리 관리**: 마이그레이션 히스토리를 확인하려면 `alembic history` 명령을 사용하세요.

4. **데이터 마이그레이션**: 스키마 변경과 함께 데이터 마이그레이션이 필요한 경우, 마이그레이션 스크립트에 데이터 변환 로직을 추가하세요.

## 다음 단계

다음 문서에서는 [스키마 정의](./04-schemas.md)에 대해 알아보겠습니다.
