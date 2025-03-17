# FastAPI RESTful API Template

FastAPI 기반의 확장 가능한 RESTful API 템플릿 프로젝트입니다. 현대적인 Python 웹 애플리케이션 개발에 필요한 다양한 기능들을 모듈화하여 제공합니다.

## 주요 기능

- 🔐 JWT 기반 인증
- 📦 모듈화된 프로젝트 구조
- 🎯 CRUD 작업을 위한 기본 엔드포인트
- 🔄 Redis 캐싱
- 📊 요청/응답 로깅
- 🛡 Rate Limiting
- 🏥 헬스 체크
- 🔒 데이터 암호화
- 🐳 Docker 지원

## 기술 스택

- **FastAPI**: 고성능 웹 프레임워크
- **PostgreSQL**: 관계형 데이터베이스
- **Redis**: 캐싱 및 세션 관리
- **SQLAlchemy**: ORM
- **Pydantic**: 데이터 검증
- **JWT**: 인증 관리
- **Docker**: 컨테이너화
- **Poetry/Pip**: 의존성 관리

## 프로젝트 구조

```
fastapi_template/
│── app/
│   ├── api/                     # API 엔드포인트
│   │   ├── routes/             # 라우터 정의
│   │   │   ├── users.py        # 사용자 관리
│   │   │   ├── items.py        # 아이템 관리
│   │   │   ├── auth.py         # 인증
│   │   │   └── __init__.py
│   │   └── dependencies.py      # 의존성 관리
│   ├── common/                  # 재사용 가능한 공통 모듈
│   │   ├── auth/               # 인증 관리
│   │   ├── cache/              # 캐시 관리
│   │   ├── config/             # 설정 관리
│   │   ├── database/           # DB 연결
│   │   ├── exceptions/         # 예외 처리
│   │   ├── middleware/         # 미들웨어
│   │   ├── monitoring/         # 상태 모니터링
│   │   ├── schemas/            # 공통 스키마
│   │   ├── security/           # 보안 기능
│   │   ├── utils/              # 유틸리티
│   │   └── validators/         # 데이터 검증
│   ├── core/                   # 핵심 설정
│   └── db/                     # 데이터베이스
├── tests/                      # 테스트 코드
├── .env.example               # 환경 변수 예시
├── docker-compose.yml         # Docker 설정
├── Dockerfile                 # Docker 빌드
└── requirements.txt           # 의존성 목록
```

## 시작하기

### 필수 요구사항

- Python 3.8+
- PostgreSQL
- Redis
- Docker (선택사항)

### 설치 방법

1. 저장소 클론

```bash
git clone https://github.com/yourusername/fastapi-template.git
cd fastapi-template
```

2. 가상환경 생성 및 활성화

```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
.\venv\Scripts\activate  # Windows
```

3. 의존성 설치

```bash
pip install -r requirements.txt
```

4. 환경 변수 설정

```bash
cp .env.example .env
# .env 파일을 적절히 수정
```

### Docker로 실행하기

```bash
docker-compose up -d
```

## API 문서

- Swagger UI: <http://localhost:8000/docs>
- ReDoc: <http://localhost:8000/redoc>

## 주요 모듈 사용법

### 인증 (Authentication)

```python
from app.common.auth.bearer import JWTBearer

@app.get("/protected", dependencies=[Depends(JWTBearer())])
async def protected_route():
    return {"message": "접근 승인됨"}
```

### 캐싱 (Caching)

```python
from app.common.cache.redis_client import cache

@cache(expire=3600)
async def get_user_data(user_id: int):
    return await db.get_user(user_id)
```

### 응답 스키마 (Response Schema)

```python
from app.common.schemas.base_schema import ResponseSchema

@app.get("/items/{item_id}")
async def get_item(item_id: int) -> ResponseSchema:
    item = await get_item_by_id(item_id)
    return ResponseSchema.success(item)
```

## 기여하기

1. Fork the Project
2. Create your Feature Branch
3. Commit your Changes
4. Push to the Branch
5. Open a Pull Request

## 라이선스

이 프로젝트는 MIT 라이선스 하에 있습니다. 자세한 내용은 [LICENSE](LICENSE) 파일을 참조하세요.
