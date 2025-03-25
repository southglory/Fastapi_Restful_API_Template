# Database 모듈 테스트 가이드

[@database](/fastapi_template/app/common/database)

## 개요

`database` 모듈은 애플리케이션의 데이터베이스 연결과 관리 기능을 구현하는 모듈입니다. SQLAlchemy를 사용하여 데이터베이스 세션, 모델, 마이그레이션 등을 제공하며, 데이터의 영구 저장소 역할을 합니다.

## 현재 모듈 구조

```
app/common/database/
├── __init__.py                 # 모듈 초기화 및 내보내기
├── database_base.py            # 기본 데이터베이스 클래스
├── database_session.py         # 세션 관리
├── database_models.py          # 데이터베이스 모델
└── database_migrations.py      # 마이그레이션 관리
```

## 테스트 용이성

- **난이도**: 중간
- **이유**:
  - 데이터베이스 연결 관리
  - 트랜잭션 처리
  - 모델 관계
  - 마이그레이션 관리

## 테스트 대상

주요 테스트 대상은 다음과 같습니다:

1. **기본 데이터베이스** (`database_base.py`)
   - 데이터베이스 초기화
   - 연결 설정
   - 공통 기능

2. **세션 관리** (`database_session.py`)
   - 세션 생성
   - 세션 관리
   - 트랜잭션 처리

3. **데이터베이스 모델** (`database_models.py`)
   - 모델 정의
   - 관계 설정
   - CRUD 작업

4. **마이그레이션** (`database_migrations.py`)
   - 마이그레이션 생성
   - 마이그레이션 실행
   - 롤백 처리

## 테스트 접근법

Database 모듈을 테스트할 때 다음 접근법을 권장합니다:

1. **단위 테스트**: 개별 데이터베이스 기능 테스트
2. **통합 테스트**: 모델과 세션 통합 테스트
3. **마이그레이션 테스트**: 스키마 변경 테스트

## 구현된 테스트 코드

각 데이터베이스 유형별 테스트 코드:

### 기본 데이터베이스 테스트

- [기본 데이터베이스 테스트 코드](/fastapi_template/tests/test_database/test_database_base.py)

### 세션 관리 테스트

- [세션 관리 테스트 코드](/fastapi_template/tests/test_database/test_database_session.py)

### 데이터베이스 모델 테스트

- [데이터베이스 모델 테스트 코드](/fastapi_template/tests/test_database/test_database_models.py)

### 마이그레이션 테스트

- [마이그레이션 테스트 코드](/fastapi_template/tests/test_database/test_database_migrations.py)

## 테스트 디렉토리 구조

테스트 파일은 다음과 같은 구조로 구성합니다:

```
tests/
└── test_database/
    ├── __init__.py
    ├── test_database_base.py
    ├── test_database_session.py
    ├── test_database_models.py
    └── test_database_migrations.py
```

## 테스트 커버리지 확인

Database 모듈의 테스트 커버리지를 확인하세요:

```bash
pytest --cov=app.common.database tests/test_database/ -v
```

## 모범 사례

1. 모든 데이터베이스 작업의 성공/실패를 테스트합니다.
2. 트랜잭션의 원자성을 검증합니다.
3. 모델 관계와 제약조건을 테스트합니다.
4. 마이그레이션의 안전성을 확인합니다.

## 주의사항

1. 실제 데이터베이스 대신 테스트용 데이터베이스를 사용합니다.
2. 각 테스트 후 데이터베이스를 초기화합니다.
3. 트랜잭션 격리 수준을 고려합니다.
4. 마이그레이션 롤백을 테스트합니다.
