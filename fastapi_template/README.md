# FastAPI RESTful API 템플릿

FastAPI를 사용한 RESTful API 개발 템플릿입니다. 사용자 인증, 데이터베이스 연동, CRUD 작업 등 기본적인 기능들이 구현되어 있어 빠르게 API 개발을 시작할 수 있습니다.

## 주요 기능

- **사용자 인증**: JWT 토큰 기반 인증
- **데이터베이스 연동**: PostgreSQL + SQLAlchemy(비동기 지원)
- **CRUD 기본 동작**: 기본적인 데이터 조작 엔드포인트
- **예외 처리**: 일관된 예외 처리 구조
- **Docker 지원**: 개발 및 배포 환경 구성 용이

## 기술 스택

- **백엔드**: FastAPI, SQLAlchemy, Pydantic
- **데이터베이스**: PostgreSQL(asyncpg)
- **컨테이너**: Docker, Docker Compose
- **인증**: JWT(python-jose)
- **문서화**: Swagger UI, ReDoc

## 시작하기

### 필요 조건

- Docker와 Docker Compose 설치
- Python 3.8 이상 (로컬 개발 시)

### 설치 및 실행

1. 저장소 클론:

   ```bash
   git clone https://github.com/username/fastapi_template.git
   cd fastapi_template
   ```

2. Docker Compose로 실행:

   ```bash
   docker-compose up -d
   ```

3. API 문서 확인:
   - Swagger UI: http://localhost:8000/docs
   - ReDoc: http://localhost:8000/redoc

### 로컬 개발 환경 구성

1. 가상 환경 생성 및 활성화:

   ```bash
   python -m venv venv
   source venv/bin/activate  # Windows: venv\Scripts\activate
   ```

2. 의존성 설치:

   ```bash
   pip install -r requirements.txt
   ```

3. 환경 변수 설정 (.env 파일 참조)

4. 개발 서버 실행:

   ```bash
   uvicorn app.main:app --reload
   ```

## 프로젝트 구조

```architecture
fastapi_template/
│── app/                       # 애플리케이션 메인 패키지
│   ├── api/                   # API 관련 모듈
│   │   ├── routes/           # 라우터 정의
│   │   ├── dependencies.py   # 의존성 주입 관리
│   ├── core/                  # 핵심 설정 모듈
│   │   ├── config.py         # 환경설정
│   │   ├── security.py       # 인증 및 보안
│   ├── db/                    # 데이터베이스 관련
│   │   ├── base.py           # SQLAlchemy 설정
│   │   ├── session.py        # DB 세션 관리
│   │   ├── models/           # DB 모델 
│   │   ├── schemas/          # Pydantic 스키마
│   ├── services/              # 비즈니스 로직
│   ├── tests/                 # 테스트 코드
│   ├── main.py                # 애플리케이션 시작점
├── .env                       # 환경 변수
├── requirements.txt           # 의존성 패키지
├── Dockerfile                 # Docker 빌드 설정
├── docker-compose.yml         # Docker Compose 설정
```

## 라이센스

MIT
