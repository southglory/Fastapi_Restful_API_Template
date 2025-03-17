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
- **Redis**: 캐싱 및 세션 관리

#### 개발 도구

- **Docker**: 컨테이너화 및 개발 환경 표준화
- **Poetry/Pip**: 의존성 관리
- **JWT**: 인증 토큰 관리 (python-jose)

## 📁 모듈 구조

```
app/
├── api/                     # API 엔드포인트
│   ├── routes/             # 라우터 정의
│   │   ├── users.py        # 사용자 관리
│   │   ├── items.py        # 아이템 관리
│   │   ├── auth.py         # 인증
│   │   └── __init__.py
│   └── dependencies.py      # 의존성 관리
├── common/                  # 재사용 가능한 공통 모듈
│   ├── auth/               # 인증 관리
│   ├── cache/              # 캐시 관리
│   ├── config/             # 설정 관리
│   ├── database/           # DB 연결 및 기본 클래스
│   │   ├── base.py         # 기본 모델 클래스
│   │   └── session.py      # DB 세션 관리
│   ├── exceptions/         # 예외 처리
│   ├── middleware/         # 미들웨어
│   ├── monitoring/         # 상태 모니터링
│   ├── schemas/            # 공통 스키마
│   │   └── base_schema.py  # 기본 스키마 클래스
│   ├── security/           # 보안 기능
│   ├── utils/             # 유틸리티
│   └── validators/         # 데이터 검증
├── core/                   # 핵심 설정
│   ├── config.py          # 환경 설정
│   └── security.py        # 보안 설정
├── db/                     # 데이터베이스
│   ├── models/            # SQLAlchemy 모델
│   │   ├── user.py        # 사용자 모델
│   │   └── item.py        # 아이템 모델
│   └── schemas/           # Pydantic 스키마
│       ├── user.py        # 사용자 스키마
│       ├── item.py        # 아이템 스키마
│       └── token.py       # 토큰 스키마
├── services/              # 비즈니스 로직
├── tests/                 # 테스트 코드
├── main.py               # 애플리케이션 진입점
└── __init__.py           # 패키지 초기화
```

## 💡 구현 가이드

### 인증 시스템

```python
from app.common.auth.bearer import JWTBearer

@app.get("/protected", dependencies=[Depends(JWTBearer())])
async def protected_route():
    return {"message": "접근 승인됨"}
```

### 캐시 시스템

```python
from app.common.cache.redis_client import cache

@cache(expire=3600)
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
from app.common.exceptions.handler import APIException

def get_user(user_id: int):
    user = db.get_user(user_id)
    if not user:
        raise APIException(status_code=404, detail="사용자를 찾을 수 없습니다")
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
DATABASE_URL=postgresql+asyncpg://user:password@localhost:5432/dbname
REDIS_URL=redis://localhost:6379/0
JWT_SECRET_KEY=your-secret-key
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
