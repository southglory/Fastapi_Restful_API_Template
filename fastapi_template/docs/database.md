# 데이터베이스 가이드

이 문서는 FastAPI 프로젝트에서 PostgreSQL 데이터베이스와 SQLAlchemy ORM을 사용한 연동 방법을 설명합니다.

## 목차

1. [데이터베이스 설정](./database/01-db-setup.md) - 연결 설정 및 세션 관리
2. [모델 정의](./database/02-models.md) - SQLAlchemy 모델 정의
3. [마이그레이션 설정](./database/03-migrations.md) - Alembic을 사용한 마이그레이션
4. [스키마 정의](./database/04-schemas.md) - Pydantic 스키마 정의
5. [서비스 레이어](./database/05-services.md) - 비즈니스 로직 구현
6. [Docker 환경 설정](./database/06-docker.md) - 컨테이너 환경 설정

## 개요

FastAPI 프로젝트에서 데이터베이스 연동은 다음과 같은 구성요소로 이루어집니다:

- **SQLAlchemy ORM**: 객체 관계 매핑을 통한 데이터베이스 접근
- **Pydantic 스키마**: 데이터 검증 및 직렬화/역직렬화
- **Alembic**: 데이터베이스 마이그레이션 관리
- **PostgreSQL**: 관계형 데이터베이스 (프로덕션 환경)
- **SQLite**: 개발 환경에서 사용할 수 있는 경량 데이터베이스
- **비동기 지원**: asyncpg 드라이버를 통한 비동기 데이터베이스 접근

각 주제에 대한 자세한 내용은 위 목차의 링크를 참조하세요.

## 시작하기

### 필요한 패키지 설치

데이터베이스 연동에 필요한 패키지를 설치합니다:

```bash
pip install sqlalchemy alembic psycopg2-binary asyncpg
```

또는 `requirements.txt`에 다음 항목을 추가합니다:

```
sqlalchemy
alembic
psycopg2-binary
asyncpg
```

### 데이터베이스 준비

#### 프로덕션 환경: PostgreSQL

1. PostgreSQL 설치 (또는 Docker 사용)
2. 데이터베이스 생성:

   ```sql
   CREATE DATABASE fastapi_db;
   ```

#### 개발 환경: SQLite

개발 환경에서는 PostgreSQL 대신 SQLite를 사용할 수 있습니다. 이를 위해 `.env.dev` 파일을 생성하고 `app/core/config.py`에 개발 환경 설정을 추가합니다.

자세한 설정 방법은 [마이그레이션 설정](./database/03-migrations.md#개발-환경-설정) 문서를 참조하세요.

### Alembic 초기화

프로젝트 루트 디렉토리에서 다음 명령을 실행하여 Alembic을 초기화합니다:

```bash
alembic init alembic
```

자세한 설정 방법은 [마이그레이션 설정](./database/03-migrations.md) 문서를 참조하세요.
