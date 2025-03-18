# 모듈 구조

```architecture
app/
├── api/                # API 엔드포인트 및 라우터
│   ├── dependencies.py # API 의존성 (인증 등)
│   └── routes/         # API 라우터
├── common/             # 공통 모듈
│   ├── auth/           # 인증 관련 기능
│   ├── cache/          # Redis 기반 캐싱 기능
│   ├── config/         # 설정 관리
│   ├── database/       # 데이터베이스 연결 및 설정
│   ├── exceptions/     # 예외 처리
│   ├── middleware/     # FastAPI 미들웨어
│   ├── monitoring/     # 애플리케이션 모니터링
│   ├── schemas/        # 공통 스키마
│   ├── security/       # 데이터 암호화 및 보안
│   ├── utils/          # 유틸리티 함수
│   └── validators/     # 데이터 유효성 검사
├── db/                 # 데이터베이스 관련
│   ├── models/         # SQLAlchemy 모델
│   └── schemas/        # Pydantic 스키마
├── services/           # 비즈니스 로직
└── main.py             # 애플리케이션 진입점
```

## 주요 모듈 설명

### API 계층 (`app/api/`)

- **routes/**: 각 도메인별 API 엔드포인트 정의
- **dependencies.py**: 인증 및 권한 검사 의존성

### 공통 모듈 (`app/common/`)

- **auth/**: JWT 인증 및 비밀번호 해싱
- **config/**: 환경 변수 및 설정 관리
- **database/**: 데이터베이스 연결 및 세션 관리
- **exceptions/**: 사용자 정의 예외 및 예외 처리기
- **schemas/**: 공통 응답 스키마
- **utils/**: 캐싱, 암호화 등 유틸리티
- **cache/**: Redis 기반 캐싱 기능 및 데코레이터
- **security/**: 데이터 암호화 및 보안 관련 유틸리티
- **middleware/**: FastAPI 미들웨어 구성요소
- **monitoring/**: 애플리케이션 모니터링 및 로깅
- **validators/**: 데이터 유효성 검사 유틸리티

### 데이터 계층 (`app/db/`)

- **models/**: SQLAlchemy ORM 모델
- **schemas/**: Pydantic 검증 스키마

### 서비스 계층 (`app/services/`)

- 비즈니스 로직 구현
- 데이터 계층과 API 계층 사이의 중간 계층
