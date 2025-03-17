# FastAPI RESTful API Template

FastAPI 기반의 확장 가능한 RESTful API 템플릿 프로젝트입니다. 현대적인 Python 웹 애플리케이션 개발에 필요한 다양한 기능들을 모듈화하여 제공하며, 빠르게 API 개발을 시작할 수 있습니다.

## 🚀 주요 특징

- 📦 **모듈형 설계**: 재사용 가능한 컴포넌트 기반
- 🔐 **보안 기능**: JWT 인증, Rate Limiting, 데이터 암호화
- 🎯 **개발 효율**: CRUD 보일러플레이트, 자동 문서화
- 🔄 **고성능**: 비동기 지원, Redis 캐싱
- 🐳 **손쉬운 배포**: Docker 기반 개발/배포 환경
- 💾 **데이터 관리**: PostgreSQL + Redis 기반 확장 가능한 데이터 계층

## 🛠 기술 스택

### 핵심 프레임워크

- FastAPI + SQLAlchemy + Pydantic
- PostgreSQL + Redis
- Docker + Docker Compose
- 비동기 지원 (async/await)

### 데이터베이스

- **메인 DB**: PostgreSQL (with asyncpg)
  - 비동기 ORM (SQLAlchemy 2.0+)
  - 자동 마이그레이션 (Alembic)
  - 커넥션 풀링
- **캐시/세션**: Redis
  - 고성능 캐싱 레이어
  - 세션 관리
  - 작업 큐

### 개발/배포

- **Docker**: 컨테이너화 및 개발 환경 표준화
- **Docker Compose**: 멀티 컨테이너 오케스트레이션
  - PostgreSQL 컨테이너
  - Redis 컨테이너
  - FastAPI 애플리케이션 컨테이너
- Poetry/Pip 의존성 관리

## ⚡️ 빠른 시작

### Docker로 시작하기

```bash
# 1. 저장소 클론
git clone https://github.com/yourusername/fastapi-template.git
cd fastapi-template

# 2. 환경 변수 설정
cp .env.example .env
# .env 파일 수정

# 3. 실행 (PostgreSQL + Redis + FastAPI)
docker-compose up -d
```

### 로컬에서 시작하기

1. **데이터베이스 준비**

```bash
# PostgreSQL 실행
docker-compose up -d postgres

# Redis 실행
docker-compose up -d redis
```

2. **애플리케이션 설정**

```bash
# Python 가상환경 설정
python -m venv venv
source venv/bin/activate  # Linux/Mac
.\venv\Scripts\activate  # Windows

# 의존성 설치
pip install -r requirements.txt

# 환경 변수 설정
cp .env.example .env
# .env 파일 수정
```

3. **데이터베이스 마이그레이션**

```bash
# 마이그레이션 실행
alembic upgrade head
```

4. **서버 실행**

```bash
uvicorn app.main:app --reload
```

## 📚 문서

- **API 문서**: <http://localhost:8000/docs>
- **상세 문서**: [기술 문서](fastapi_template/README.md)
- **데이터베이스 문서**: [DB 설계](docs/database.md)

## 💾 데이터베이스 구성

### PostgreSQL 구성

- 기본 포트: 5432
- 데이터베이스: fastapi_db
- 기본 스키마:
  - users: 사용자 관리
  - items: 기본 CRUD 예제
  - audit: 감사 로그

### Redis 구성

- 기본 포트: 6379
- 데이터베이스:
  - DB 0: 캐시
  - DB 1: 세션
  - DB 2: 작업 큐

## 🤝 기여하기

프로젝트 기여는 언제나 환영합니다! 자세한 내용은 [기여 가이드](CONTRIBUTING.md)를 참조해주세요.

## 📄 라이선스

이 프로젝트는 MIT 라이선스를 따릅니다. 자세한 내용은 [LICENSE](LICENSE) 파일을 참조하세요.

## 📁 프로젝트 구조

```
fastapi_template/
├── app/                      # 애플리케이션 코드
│   ├── api/                  # API 엔드포인트
│   │   ├── routes/          # 라우터 정의
│   │   │   ├── users.py     # 사용자 관리
│   │   │   ├── items.py     # 아이템 관리
│   │   │   ├── auth.py      # 인증
│   │   │   └── __init__.py
│   │   └── dependencies.py   # 의존성 관리
│   ├── common/               # 재사용 가능한 공통 모듈
│   │   ├── auth/            # 인증 관리
│   │   ├── cache/           # 캐시 관리
│   │   ├── config/          # 설정 관리
│   │   ├── database/        # DB 연결 및 기본 클래스
│   │   │   ├── base.py      # 기본 모델 클래스
│   │   │   └── session.py   # DB 세션 관리
│   │   ├── exceptions/      # 예외 처리
│   │   ├── middleware/      # 미들웨어
│   │   ├── monitoring/      # 상태 모니터링
│   │   ├── schemas/         # 공통 스키마
│   │   │   └── base_schema.py # 기본 스키마 클래스
│   │   ├── security/        # 보안 기능
│   │   ├── utils/          # 유틸리티
│   │   └── validators/      # 데이터 검증
│   ├── core/                # 핵심 설정
│   │   ├── config.py       # 환경 설정
│   │   └── security.py     # 보안 설정
│   ├── db/                  # 데이터베이스
│   │   ├── models/         # SQLAlchemy 모델
│   │   │   ├── user.py     # 사용자 모델
│   │   │   └── item.py     # 아이템 모델
│   │   └── schemas/        # Pydantic 스키마
│   │       ├── user.py     # 사용자 스키마
│   │       ├── item.py     # 아이템 스키마
│   │       └── token.py    # 토큰 스키마
│   ├── services/           # 비즈니스 로직
│   ├── tests/              # 테스트 코드
│   ├── main.py            # 애플리케이션 진입점
│   └── __init__.py        # 패키지 초기화
├── .env.example           # 환경 변수 예시
├── docker-compose.yml     # Docker 설정
├── Dockerfile             # Docker 빌드
└── requirements.txt       # 의존성 목록
```

### 향후 추가 예정 구조

다음 구조들은 개발 진행 중에 추가될 예정입니다:

```
fastapi_template/
├── app/
│   └── tests/
│       ├── conftest.py    # 테스트 설정
│       ├── unit/          # 단위 테스트
│       └── integration/   # 통합 테스트
├── alembic/               # DB 마이그레이션
│   ├── versions/         # 마이그레이션 파일
│   └── env.py           # Alembic 설정
├── docs/                  # 문서
│   └── database.md       # DB 설계 문서
└── alembic.ini           # Alembic 설정
```
