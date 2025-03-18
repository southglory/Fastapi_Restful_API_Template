# 테스트 실행 방법

이 문서는 FastAPI 템플릿 프로젝트의 테스트를 실행하는 다양한 방법을 설명합니다.

## 사전 요구사항

테스트를 실행하기 전에 다음 요구사항을 충족해야 합니다:

1. 가상 환경이 활성화되어 있어야 합니다.
2. 필요한 모든 의존성이 설치되어 있어야 합니다: `pip install -r requirements-dev.txt`
3. 환경 변수가 올바르게 설정되어 있어야 합니다 (`.env.test` 파일 사용 권장).

## 기본 테스트 실행

모든 테스트를 실행하려면:

```bash
# 프로젝트 루트 디렉토리에서
pytest
```

## 특정 테스트 파일 실행

특정 테스트 파일만 실행하려면:

```bash
# 특정 파일 실행
pytest tests/test_common_modules.py

# 특정 디렉토리의 모든 테스트 실행
pytest tests/test_api/
```

## 특정 테스트 함수 실행

특정 테스트 함수만 실행하려면:

```bash
# 특정 테스트 함수 실행
pytest tests/test_common_modules.py::test_config_module

# 특정 함수 이름 패턴으로 테스트 실행
pytest -k "config or auth"
```

## 테스트 출력 상세도 조절

테스트 출력의 상세도를 조절하려면:

```bash
# 자세한 출력
pytest -v

# 매우 자세한 출력
pytest -vv

# 실패한 테스트만 출력
pytest --no-header --no-summary -q
```

## 테스트 커버리지 측정

코드 커버리지를 측정하려면:

```bash
# 기본 커버리지 측정
pytest --cov=app tests/

# 커버리지 보고서 HTML 형식으로 생성
pytest --cov=app --cov-report=html tests/

# 커버리지 보고서 XML 형식으로 생성 (CI 통합용)
pytest --cov=app --cov-report=xml tests/
```

## 병렬 테스트 실행

테스트를 병렬로 실행하려면:

```bash
# 4개의 프로세스로 병렬 실행
pytest -n 4
```

## 테스트 로깅 설정

테스트 중 로그 출력을 보려면:

```bash
# 로그 레벨 설정
pytest --log-cli-level=INFO

# 로그 출력을 파일에 저장
pytest --log-file=test_log.txt
```

## 비동기 테스트 실행

비동기 테스트를 실행하려면:

```bash
# pytest-asyncio 사용
pytest --asyncio-mode=auto
```

## 데이터베이스 테스트

데이터베이스 테스트를 위해 인메모리 데이터베이스를 사용하려면 환경 변수를 설정하세요:

```bash
# SQLite 인메모리 데이터베이스 사용
export DATABASE_URL=sqlite:///./test.db
```

또는 `.env.test` 파일에 다음을 추가하세요:

```
DATABASE_URL=sqlite:///./test.db
```

## CI 환경에서 테스트 실행

CI 환경에서는 다음과 같은 명령을 사용하는 것이 좋습니다:

```bash
pytest --cov=app --cov-report=xml --junitxml=test-results.xml
```

이 명령은 코드 커버리지 보고서와 테스트 결과를 CI 도구에서 처리할 수 있는 형식으로 생성합니다.
