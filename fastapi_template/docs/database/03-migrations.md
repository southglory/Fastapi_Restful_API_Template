# 마이그레이션 설정

이 문서는 FastAPI 프로젝트에서 Alembic을 사용한 데이터베이스 마이그레이션 설정 방법을 설명합니다.

## 목차

1. [Alembic 소개](#alembic-소개)
2. [Alembic 설치](#alembic-설치)
3. [초기 설정](#초기-설정)
4. [마이그레이션 파일 생성](#마이그레이션-파일-생성)
5. [마이그레이션 적용](#마이그레이션-적용)
6. [마이그레이션 롤백](#마이그레이션-롤백)

## Alembic 소개

Alembic은 SQLAlchemy를 위한 데이터베이스 마이그레이션 도구입니다. 데이터베이스 스키마 변경 사항을 버전 관리하고 적용할 수 있습니다.

주요 기능:

- 데이터베이스 스키마 변경 이력 관리
- 자동 마이그레이션 스크립트 생성
- 마이그레이션 적용 및 롤백

## Alembic 설치

### 패키지 설치

Alembic은 pip를 사용하여 설치할 수 있습니다:

```bash
pip install alembic
```

프로젝트의 `requirements.txt`에 추가하는 것이 좋습니다:

```
# requirements.txt
alembic
```

### 설치 확인

설치가 완료되면 다음 명령으로 Alembic 버전을 확인할 수 있습니다:

```bash
alembic --version
```

## 초기 설정

### 1. Alembic 초기화

프로젝트 루트 디렉토리에서 다음 명령을 실행합니다:

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

각 파일의 역할:

- `alembic.ini`: Alembic 설정 파일
- `alembic/env.py`: 마이그레이션 환경 설정
- `alembic/versions/`: 마이그레이션 스크립트 저장 디렉토리
- `alembic/script.py.mako`: 마이그레이션 스크립트 템플릿

### 2. Alembic 설정 파일 수정

`alembic.ini` 파일에서 데이터베이스 URL을 설정합니다:

```ini
# alembic.ini
[alembic]
# ...
sqlalchemy.url = postgresql://postgres:postgres@localhost:5432/fastapi_db
```

또는 환경 변수에서 URL을 가져오도록 설정할 수 있습니다:

```ini
# alembic.ini
[alembic]
# ...
# sqlalchemy.url = driver://user:pass@localhost/dbname
```

이 경우 `env.py`에서 URL을 설정합니다.

### 3. Alembic 환경 설정

`alembic/env.py` 파일을 수정하여 SQLAlchemy 모델을 인식하도록 설정합니다:

```python
# alembic/env.py
from logging.config import fileConfig

from sqlalchemy import engine_from_config, pool

from alembic import context

# 모델 가져오기
from app.common.database.base import Base
from app.db.models import User, Item  # 모든 모델 가져오기

# this is the Alembic Config object
config = context.config

# DB URL을 환경 변수에서 가져오기
from app.core.config import settings
config.set_main_option("sqlalchemy.url", settings.DATABASE_URL)

# Interpret the config file for Python logging
fileConfig(config.config_file_name)

# MetaData 객체 설정
target_metadata = Base.metadata

# ...
```

### 4. Python 경로 설정

Alembic이 애플리케이션 모듈을 찾을 수 있도록 Python 경로를 설정해야 할 수 있습니다. 이는 `PYTHONPATH` 환경 변수를 설정하거나 다음과 같이 `env.py` 파일을 수정하여 수행할 수 있습니다:

```python
# alembic/env.py
import os
import sys
from pathlib import Path

# 프로젝트 루트 디렉토리를 Python 경로에 추가
sys.path.append(str(Path(__file__).parent.parent))

# 나머지 코드...
```

## 마이그레이션 파일 생성

### 자동 마이그레이션 파일 생성

모델 변경 사항을 감지하여 자동으로 마이그레이션 파일을 생성합니다:

```bash
alembic revision --autogenerate -m "설명"
```

예시:

```bash
alembic revision --autogenerate -m "Create user and item tables"
```

이 명령은 `alembic/versions/` 디렉토리에 새로운 마이그레이션 파일을 생성합니다:

```python
# alembic/versions/1a2b3c4d5e6f_create_user_and_item_tables.py
"""Create user and item tables

Revision ID: 1a2b3c4d5e6f
Revises: 
Create Date: 2023-01-01 12:00:00.000000

"""
from alembic import op
import sqlalchemy as sa

# ...

def upgrade():
    # 테이블 생성 코드
    op.create_table(
        'user',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('email', sa.String(), nullable=False),
        # ...
        sa.PrimaryKeyConstraint('id')
    )
    # ...

def downgrade():
    # 테이블 삭제 코드
    op.drop_table('item')
    op.drop_table('user')
```

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

## 다음 단계

다음 문서에서는 [스키마 정의](./04-schemas.md)에 대해 알아보겠습니다.
