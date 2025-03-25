# Schemas 모듈 테스트 가이드

[@schemas](/fastapi_template/app/common/schemas)

## 개요

`schemas` 모듈은 애플리케이션의 데이터 모델을 정의하는 모듈입니다. Pydantic을 사용하여 API 요청/응답, 데이터베이스 모델, 검증 규칙 등을 정의하며, 데이터의 유효성 검증과 직렬화/역직렬화를 담당합니다.

## 현재 모듈 구조

```
app/common/schemas/
├── __init__.py                 # 모듈 초기화 및 내보내기
├── schemas_base.py             # 기본 스키마 클래스
├── schemas_user.py             # 사용자 관련 스키마
├── schemas_auth.py             # 인증 관련 스키마
└── schemas_item.py             # 아이템 관련 스키마
```

## 테스트 용이성

- **난이도**: 쉬움
- **이유**:
  - Pydantic의 내장 검증 기능 활용
  - 명확한 데이터 구조 정의
  - 외부 의존성 없음
  - 결정적 동작

## 테스트 대상

주요 테스트 대상은 다음과 같습니다:

1. **기본 스키마** (`schemas_base.py`)
   - 기본 스키마 클래스
   - 공통 필드 정의
   - 기본 검증 규칙

2. **사용자 스키마** (`schemas_user.py`)
   - 사용자 생성 스키마
   - 사용자 업데이트 스키마
   - 사용자 응답 스키마

3. **인증 스키마** (`schemas_auth.py`)
   - 로그인 스키마
   - 토큰 스키마
   - 비밀번호 변경 스키마

4. **아이템 스키마** (`schemas_item.py`)
   - 아이템 생성 스키마
   - 아이템 업데이트 스키마
   - 아이템 응답 스키마

## 테스트 접근법

Schemas 모듈을 테스트할 때 다음 접근법을 권장합니다:

1. **단위 테스트**: 개별 스키마 클래스 테스트
2. **검증 테스트**: 필드 검증 규칙 테스트
3. **변환 테스트**: 직렬화/역직렬화 테스트

## 구현된 테스트 코드

Schemas 모듈의 테스트 코드:

- [기본 스키마 테스트](/fastapi_template/tests/test_schemas/test_base_schema.py)
- [스키마 변환 테스트](/fastapi_template/tests/test_schemas/test_schema_conversion.py)
- [스키마 예제 테스트](/fastapi_template/tests/test_schemas/test_schema_examples.py)
- [페이지네이션 스키마 테스트](/fastapi_template/tests/test_schemas/test_pagination_schema.py)

## 테스트 디렉토리 구조

테스트 파일은 다음과 같은 구조로 구성합니다:

```
tests/
└── test_schemas/
    ├── __init__.py
    ├── test_base_schema.py
    ├── test_schema_conversion.py
    ├── test_schema_examples.py
    └── test_pagination_schema.py
```

## 테스트 커버리지 확인

Schemas 모듈의 테스트 커버리지를 확인하세요:

```bash
pytest --cov=app.common.schemas tests/test_schemas/ -v
```

## 모범 사례

1. 모든 필드의 유효성 검증을 테스트합니다.
2. 기본값과 선택적 필드를 검증합니다.
3. 중첩된 스키마의 검증을 테스트합니다.
4. 에러 메시지의 정확성을 확인합니다.

## 주의사항

1. Pydantic의 내장 검증은 테스트하지 않습니다.
2. 순환 참조를 피합니다.
3. 스키마 버전 호환성을 유지합니다.
4. 성능에 영향을 주는 복잡한 검증을 피합니다.
