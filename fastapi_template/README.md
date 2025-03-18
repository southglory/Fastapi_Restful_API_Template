# FastAPI RESTful API 기술 문서

이 문서는 FastAPI 템플릿의 상세 기술 명세와 구현 가이드를 제공합니다.

## 📋 목차

- [아키텍처](#아키텍처)
- [모듈 구조](#모듈-구조)
- [구현 가이드](#구현-가이드)
- [API 참조](#api-참조)
- [개발 가이드](#개발-가이드)

## 🏗 아키텍처

### 계층형 아키텍처

```
프레젠테이션 계층 (API Layer)
    │
서비스 계층 (Business Layer)
    │
데이터 계층 (Data Layer)
```

### 기술 스택 상세

#### 백엔드 프레임워크

- **FastAPI**: 고성능 비동기 웹 프레임워크
- **SQLAlchemy**: 비동기 지원 ORM
- **Pydantic**: 데이터 검증 및 설정 관리

#### 데이터베이스

- **PostgreSQL**: 메인 데이터베이스 (with asyncpg)
- **SQLite**: 개발 및 테스트용 데이터베이스 (with aiosqlite)
- **Redis**: 캐싱 및 세션 관리

#### 개발 도구

- **Docker**: 컨테이너화 및 개발 환경 표준화
- **Poetry/Pip**: 의존성 관리
- **JWT**: 인증 토큰 관리 (python-jose)

## 📁 모듈 구조

프로젝트의 상세한 디렉토리 구조는 [py_project_tree.txt](py_project_tree.txt)를 참조하세요.

주요 디렉토리 설명:

- `app/api/`: API 엔드포인트와 라우터
- `app/common/`: 재사용 가능한 공통 모듈
  - `app/common/auth/`: 인증 관련 기능
  - `app/common/config/`: 애플리케이션 설정
  - `app/common/database/`: 데이터베이스 연결 및 기본 설정
  - `app/common/exceptions/`: 예외 처리
  - `app/common/schemas/`: 공통 스키마
  - `app/common/utils/`: 유틸리티 함수
- `app/db/`: 데이터베이스 모델과 스키마
  - `app/db/models/`: SQLAlchemy 모델
  - `app/db/schemas/`: Pydantic 스키마
- `app/services/`: 비즈니스 로직
- `app/tests/`: 테스트 코드

## 💡 구현 가이드

### 인증 시스템

```python
from app.common.auth import JWTBearer

@app.get("/protected", dependencies=[Depends(JWTBearer())])
async def protected_route():
    return {"message": "접근 승인됨"}
```

### 캐시 시스템

```python
from app.common.utils.cache import cached

@cached(prefix="user_data", ttl=3600)
async def get_user_data(user_id: int):
    return await db.get_user(user_id)
```

### 응답 처리

```python
from app.common.schemas.base_schema import ResponseSchema

@app.get("/items/{item_id}")
async def get_item(item_id: int) -> ResponseSchema:
    item = await get_item_by_id(item_id)
    return ResponseSchema.success(item)
```

### 예외 처리

```python
from app.common.exceptions import AuthenticationError

def get_user(user_id: int):
    user = db.get_user(user_id)
    if not user:
        raise AuthenticationError("사용자를 찾을 수 없습니다")
    return user
```

## 🔌 API 참조

### 엔드포인트

- `POST /api/auth/login`: 로그인
- `POST /api/auth/refresh`: 토큰 갱신
- `GET /api/users/me`: 현재 사용자 정보
- `GET /api/health`: 시스템 상태 체크

### 응답 형식

```json
{
    "success": true,
    "message": "Success",
    "data": {
        "id": 1,
        "username": "test_user"
    }
}
```

## 👨‍💻 개발 가이드

### 새로운 API 엔드포인트 추가

1. `app/api/routes/` 디렉토리에 새 라우터 파일 생성
2. 공통 응답 스키마 사용
3. 적절한 예외 처리 추가
4. API 문서화 (FastAPI 자동 문서화)

### 환경 변수 설정

필수 환경 변수:

```env
# PostgreSQL 설정
DATABASE_URL=postgresql://user:password@localhost:5432/dbname
# 또는 SQLite 설정 (개발/테스트 환경)
# DATABASE_URL=sqlite:///./dev.db

# Redis 설정
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_DB=0

# 보안 설정
SECRET_KEY=your-secret-key
```

### 테스트

```bash
# 단위 테스트 실행
pytest tests/unit

# 통합 테스트 실행
pytest tests/integration

# 전체 테스트 실행
pytest
```

## 라이센스

MIT
