# 테스트 도구 가이드

이 문서는 FastAPI 템플릿 프로젝트에서 사용되는 테스트 도구와 유틸리티에 대한 자세한 정보를 제공합니다.

## 목차

- [테스트 실행기](#테스트-실행기)
- [테스트 지원 도구](#테스트-지원-도구)
- [코드 품질 도구](#코드-품질-도구)
- [API 테스트 도구](#api-테스트-도구)
- [부하 테스트 도구](#부하-테스트-도구)
- [테스트 관리 도구](#테스트-관리-도구)

## 테스트 실행기

### pytest

**설명**: FastAPI 템플릿 프로젝트의 주요 테스트 프레임워크

**기본 사용법**:

```bash
# 모든 테스트 실행
pytest

# 특정 테스트 파일 실행
pytest tests/test_basic.py

# 특정 테스트 함수 실행
pytest tests/test_basic.py::test_function_name

# 마커로 테스트 필터링
pytest -m "unit"
```

**플러그인 및 확장**:

| 플러그인 | 설명 | 문서 링크 |
|----------|------|----------|
| pytest-cov | 코드 커버리지 리포트 생성 | [문서](https://pytest-cov.readthedocs.io/) |
| pytest-xdist | 병렬 테스트 실행 | [문서](https://github.com/pytest-dev/pytest-xdist) |
| pytest-asyncio | 비동기 테스트 지원 | [문서](https://github.com/pytest-dev/pytest-asyncio) |
| pytest-env | 환경 변수 설정 | [문서](https://github.com/MobileDynasty/pytest-env) |
| pytest-timeout | 테스트 타임아웃 설정 | [문서](https://github.com/pytest-dev/pytest-timeout) |

**고급 설정**:

`pytest.ini` 설정 파일 예시:
```ini
[pytest]
testpaths = tests
python_files = test_*.py
python_functions = test_*
markers =
    unit: Unit tests
    integration: Integration tests
    api: API tests
    slow: Slow running tests
    dependency: Dependency tests
filterwarnings =
    ignore::DeprecationWarning
```

## 테스트 지원 도구

### Pytest Fixtures

**설명**: 테스트에 필요한 의존성과 상태를 제공하는 모듈화된 메커니즘

**기본 예제**:

```python
# conftest.py
import pytest
from fastapi.testclient import TestClient
from app.main import app

@pytest.fixture
def client():
    """테스트용 FastAPI 클라이언트 반환"""
    return TestClient(app)

@pytest.fixture
def db_session():
    """테스트 데이터베이스 세션 제공"""
    from app.database import get_test_db
    db = get_test_db()
    yield db
    db.close()
```

**사용 패턴**:

```python
def test_read_main(client):
    response = client.get("/")
    assert response.status_code == 200
```

**공통 fixture 위치**:
- 프로젝트 전체: `tests/conftest.py`
- 모듈별: `tests/module_name/conftest.py`

### Test Factories

**설명**: 테스트 데이터 생성을 위한 도우미 함수 및 클래스

**권장 라이브러리**: 
- [Factory Boy](https://factoryboy.readthedocs.io/)
- [Faker](https://faker.readthedocs.io/)

**예제**:

```python
# factories.py
import factory
from app.models import User
from app.database import get_db

class UserFactory(factory.alchemy.SQLAlchemyModelFactory):
    class Meta:
        model = User
        sqlalchemy_session = get_db()
        sqlalchemy_session_persistence = "commit"

    username = factory.Faker('user_name')
    email = factory.Faker('email')
    full_name = factory.Faker('name')
```

**사용 방법**:

```python
def test_user_creation():
    user = UserFactory()
    assert user.id is not None
    assert '@' in user.email
```

## 코드 품질 도구

### pytest-cov

**설명**: 코드 커버리지 측정 및 리포트 생성 도구

**설치**: `pip install pytest-cov`

**기본 사용법**:
```bash
# 전체 테스트 실행 및 커버리지 리포트 생성
pytest --cov=app tests/

# HTML 형식 리포트 생성
pytest --cov=app --cov-report=html tests/

# XML 형식 리포트 생성 (CI 도구용)
pytest --cov=app --cov-report=xml tests/
```

**설정 파일 예시**:
```ini
# .coveragerc
[run]
source = app
omit = */migrations/*, */tests/*

[report]
exclude_lines =
    pragma: no cover
    def __repr__
    raise NotImplementedError
```

### mypy

**설명**: 정적 타입 검사기

**설치**: `pip install mypy`

**사용법**:
```bash
# 전체 프로젝트 타입 체크
mypy app/

# 특정 파일 타입 체크
mypy app/models.py
```

**설정 파일 예시**:
```ini
# mypy.ini
[mypy]
python_version = 3.9
warn_return_any = True
warn_unused_configs = True
disallow_untyped_defs = True
disallow_incomplete_defs = True

[mypy.plugins.sqlalchemy.ext]
fully_qualified_type_names = True
```

### pylint & flake8

**설명**: 코드 품질 및 스타일 검사 도구

**설치**: `pip install pylint flake8`

**사용법**:
```bash
# pylint 실행
pylint app/

# flake8 실행
flake8 app/
```

## API 테스트 도구

### FastAPI TestClient

**설명**: FastAPI의 내장 테스트 클라이언트

**기본 사용법**:
```python
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_read_main():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": "Hello World"}
```

**고급 기능**:
- 헤더 설정: `client.get("/users/me", headers={"Authorization": "Bearer token"})`
- JSON 데이터 전송: `client.post("/items/", json={"name": "Foo", "price": 10.5})`
- 파일 업로드: `client.post("/upload/", files={"file": ("filename.txt", open("file.txt", "rb"))})`
- 쿠키 설정: `client.get("/cookie-protected", cookies={"session": "value"})`

### requests-mock

**설명**: 외부 API 요청 모킹 라이브러리

**설치**: `pip install requests-mock`

**사용법**:
```python
import requests
import requests_mock

def test_external_api_call():
    with requests_mock.Mocker() as m:
        m.get('http://external-api.com/data', json={'key': 'value'})
        response = requests.get('http://external-api.com/data')
        assert response.json() == {'key': 'value'}
```

## 부하 테스트 도구

### Locust

**설명**: 사용자 친화적인 분산 부하 테스트 도구

**설치**: `pip install locust`

**기본 사용법**:
```python
# locustfile.py
from locust import HttpUser, task, between

class WebsiteUser(HttpUser):
    wait_time = between(1, 5)
    
    @task
    def index_page(self):
        self.client.get("/")
        
    @task(3)
    def view_items(self):
        self.client.get("/items")
```

**실행 명령어**:
```bash
locust -f locustfile.py
```

웹 인터페이스: http://localhost:8089

### Apache JMeter

**설명**: 고급 부하 테스트 및 성능 측정 도구

**다운로드**: [JMeter 공식 사이트](https://jmeter.apache.org/download_jmeter.cgi)

**사용법**:
1. JMeter GUI를 통해 테스트 계획 작성
2. 테스트 요소 추가 (스레드 그룹, HTTP 요청, 리스너 등)
3. 테스트 실행 및 결과 분석

## 테스트 관리 도구

### pytest-html

**설명**: HTML 형식의 테스트 리포트 생성 도구

**설치**: `pip install pytest-html`

**사용법**:
```bash
pytest --html=report.html --self-contained-html
```

### pytest-xdist

**설명**: 병렬 테스트 실행을 위한 pytest 플러그인

**설치**: `pip install pytest-xdist`

**사용법**:
```bash
# CPU 코어 수만큼 병렬 실행
pytest -n auto

# 특정 수의 병렬 프로세스 지정
pytest -n 4
```

### tox

**설명**: 여러 Python 버전에서 테스트 실행을 자동화하는 도구

**설치**: `pip install tox`

**설정 파일 예시**:
```ini
# tox.ini
[tox]
envlist = py38, py39, py310

[testenv]
deps =
    pytest
    pytest-cov
commands =
    pytest --cov=app tests/
```

**실행 명령어**:
```bash
tox
```

## 관련 문서

- [테스트 개요 및 구조](01-test_overview.md)
- [테스트 시작 및 실행 가이드](02-test_guide.md)
- [테스트 모범 사례 및 패턴](03-test_practices.md)
- [모듈별 테스트 가이드](04-test_modules.md) 