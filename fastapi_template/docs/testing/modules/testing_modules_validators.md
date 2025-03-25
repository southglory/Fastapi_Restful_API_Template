# Validators 모듈 테스트 가이드

[@validators](/fastapi_template/app/common/validators)

## 개요

`validators` 모듈은 애플리케이션의 데이터 검증을 구현하는 모듈입니다. 이메일, 비밀번호, 전화번호, URL 등의 데이터 유효성을 검증하며, 사용자 입력의 안전성과 정확성을 보장합니다.

## 현재 모듈 구조

```
app/common/validators/
├── __init__.py                 # 모듈 초기화 및 내보내기
├── validators_base.py          # 기본 검증기 클래스
├── validators_email.py         # 이메일 검증
├── validators_password.py      # 비밀번호 검증
└── validators_phone.py         # 전화번호 검증
```

## 테스트 용이성

- **난이도**: 쉬움-중간
- **이유**:
  - 순수 검증 함수
  - 명확한 입력/출력
  - 외부 의존성 없음
  - 다양한 케이스 테스트 필요

## 테스트 대상

주요 테스트 대상은 다음과 같습니다:

1. **기본 검증기** (`validators_base.py`)
   - 기본 검증 클래스
   - 공통 검증 메서드
   - 에러 메시지 처리

2. **이메일 검증** (`validators_email.py`)
   - 이메일 형식 검증
   - 도메인 검증
   - 특수 문자 처리

3. **비밀번호 검증** (`validators_password.py`)
   - 비밀번호 강도 검증
   - 특수 문자 요구사항
   - 최소 길이 검증

4. **전화번호 검증** (`validators_phone.py`)
   - 전화번호 형식 검증
   - 국가 코드 처리
   - 특수 문자 처리

## 테스트 접근법

Validators 모듈을 테스트할 때 다음 접근법을 권장합니다:

1. **단위 테스트**: 개별 검증 함수 테스트
2. **경계값 테스트**: 유효/무효 경계값 테스트
3. **특수 케이스 테스트**: 특수 문자, 유니코드 등 테스트

## 구현된 테스트 코드

Validators 모듈의 테스트 코드:

- [문자열 검증 테스트](/fastapi_template/tests/test_validators/test_string_validators.py)
- [데이터 검증 테스트](/fastapi_template/tests/test_validators/test_data_validators.py)
- [파일 검증 테스트](/fastapi_template/tests/test_validators/test_file_validators.py)

## 테스트 디렉토리 구조

테스트 파일은 다음과 같은 구조로 구성합니다:

```
tests/
└── test_validators/
    ├── __init__.py
    ├── test_string_validators.py
    ├── test_data_validators.py
    └── test_file_validators.py
```

## 테스트 커버리지 확인

Validators 모듈의 테스트 커버리지를 확인하세요:

```bash
pytest --cov=app.common.validators tests/test_validators/ -v
```

## 모범 사례

1. 모든 유효성 검증 규칙을 테스트합니다.
2. 경계값과 예외 케이스를 포함합니다.
3. 에러 메시지의 정확성을 확인합니다.
4. 유니코드 지원을 검증합니다.

## 주의사항

1. 정규식 패턴의 정확성을 검증합니다.
2. 성능에 영향을 주는 복잡한 검증을 피합니다.
3. 국제화 지원을 고려합니다.
4. 에러 메시지의 일관성을 유지합니다.
