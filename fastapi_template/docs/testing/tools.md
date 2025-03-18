# 테스트 도구 가이드

이 문서는 FastAPI 템플릿 프로젝트에서 사용되는 테스트 도구와 라이브러리에 대한 정보를 제공합니다.

## 테스트 라이브러리

### pytest

[pytest](https://docs.pytest.org/)는 이 프로젝트의 기본 테스트 프레임워크입니다.

#### 주요 기능

- 간결한 테스트 케이스 작성
- 풍부한 플러그인 생태계
- 강력한 fixture 시스템
- 자세한 실패 보고서
- 파라미터화된 테스트 지원

#### 설치

```bash
pip install pytest
```

#### 기본 사용법

```python
# 기본 테스트 함수
def test_addition():
    assert 1 + 1 == 2

# 클래스 기반 테스트
class TestExample:
    def test_method(self):
        assert "hello".upper() == "HELLO"
    
    def test_another_method(self):
        assert len([1, 2, 3]) == 3
```

### pytest-asyncio

[pytest-asyncio](https://pytest-asyncio.readthedocs.io/)는 비동기 코드 테스트를 위한 pytest 플러그인입니다.

#### 주요 기능

- 비동기 테스트 함수 지원
- 비동기 fixture 지원
- 다양한 이벤트 루프 정책 지원

#### 설치

```bash
pip install pytest-asyncio
```

#### 기본 사용법

```python
import pytest

@pytest.mark.asyncio
async def test_async_function():
    result = await some_async_function()
    assert result == expected_value

# 비동기 fixture
@pytest.fixture
async def async_fixture():
    # 비동기 설정
    resource = await async_setup()
    yield resource
    # 비동기 정리
    await async_cleanup(resource)
```

### pytest-cov

[pytest-cov](https://pytest-cov.readthedocs.io/)는 코드 커버리지 측정을 위한 pytest 플러그인입니다.

#### 주요 기능

- 테스트 코드 커버리지 측정
- 다양한 보고서 형식 지원 (터미널, HTML, XML)
- 특정 파일 또는 디렉토리에 대한 커버리지 측정 가능

#### 설치

```bash
pip install pytest-cov
```

#### 기본 사용법

```bash
# 기본 커버리지 측정
pytest --cov=app tests/

# HTML 보고서 생성
pytest --cov=app --cov-report=html tests/

# 특정 디렉토리만 측정
pytest --cov=app.common.validators tests/test_validators/
```

### FastAPI TestClient

FastAPI는 `TestClient` 클래스를 제공하여 API 엔드포인트 테스트를 쉽게 할 수 있습니다.

#### 주요 기능

- HTTP 요청 시뮬레이션
- 응답 검증
- 쿠키 및 세션 지원

#### 설치

```bash
# FastAPI와 함께 자동으로 설치됨
pip install fastapi
```

#### 기본 사용법

```python
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_read_main():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": "Hello World"}

def test_create_item():
    response = client.post(
        "/items/",
        json={"name": "Test Item", "price": 10.5}
    )
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "Test Item"
    assert data["price"] == 10.5
```

## 모킹 도구

### unittest.mock

Python의 표준 라이브러리인 `unittest.mock`은 테스트에서 모의 객체를 생성하는 데 사용됩니다.

#### 주요 기능

- 함수 및 메서드 모킹
- 속성 값 설정
- 함수 호출 추적
- 반환 값 지정

#### 기본 사용법

```python
from unittest.mock import patch, MagicMock

# 함수 패치
@patch('module.function')
def test_function(mock_function):
    mock_function.return_value = 'mocked_value'
    assert module.function() == 'mocked_value'
    mock_function.assert_called_once()

# 클래스 패치
@patch('module.ClassName')
def test_class(MockClass):
    module.ClassName.return_value.some_method.return_value = 'mocked_value'
    instance = module.ClassName()
    assert instance.some_method() == 'mocked_value'

# with 문으로 패치
def test_with_patch():
    with patch('module.function') as mock_function:
        mock_function.return_value = 'mocked_value'
        assert module.function() == 'mocked_value'
```

### pytest-mock

[pytest-mock](https://pytest-mock.readthedocs.io/)은 pytest에서 모킹을 더 쉽게 할 수 있는 플러그인입니다.

#### 주요 기능

- unittest.mock의 기능을 pytest와 통합
- mocker fixture 제공
- 자동 정리 지원

#### 설치

```bash
pip install pytest-mock
```

#### 기본 사용법

```python
def test_with_mocker(mocker):
    # 함수 모킹
    mock_function = mocker.patch('module.function')
    mock_function.return_value = 'mocked_value'
    
    # 특성 모킹
    mocker.patch.object(SomeClass, 'class_method', return_value='mocked')
    
    # 스파이 생성
    spy = mocker.spy(SomeClass, 'instance_method')
    
    # 어서션
    SomeClass().instance_method(1, 2)
    spy.assert_called_once_with(mocker.ANY, 1, 2)
```

## 데이터베이스 테스트 도구

### SQLAlchemy

SQLAlchemy는 ORM을 통한 데이터베이스 테스트에 사용됩니다.

#### 테스트용 인메모리 데이터베이스 설정

```python
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.db.base import Base

# 인메모리 SQLite 데이터베이스
engine = create_engine("sqlite:///:memory:")
Base.metadata.create_all(engine)
SessionLocal = sessionmaker(bind=engine)
session = SessionLocal()

# 테스트 후 정리
session.close()
Base.metadata.drop_all(engine)
```

### alembic

alembic은 데이터베이스 마이그레이션 테스트에 사용됩니다.

#### 테스트용 마이그레이션 실행

```python
import subprocess
from pathlib import Path

def test_migrations():
    # 테스트 환경 설정
    os.environ["DATABASE_URL"] = "sqlite:///./test.db"
    
    # 마이그레이션 실행
    subprocess.run(["alembic", "upgrade", "head"], check=True)
    
    # 마이그레이션 검증 테스트
    # ...
    
    # 정리
    Path("./test.db").unlink()
```

## HTTP 요청 모킹

### respx

[respx](https://lundberg.github.io/respx/)는 httpx 요청을 모킹하는 데 사용됩니다.

#### 설치

```bash
pip install respx
```

#### 기본 사용법

```python
import httpx
import respx
import pytest

@pytest.mark.asyncio
async def test_with_respx_router():
    with respx.mock:
        # 요청 모킹
        respx.get("https://example.com/api").respond(
            status_code=200,
            json={"data": "mocked response"}
        )
        
        # 비동기 클라이언트로 요청
        async with httpx.AsyncClient() as client:
            response = await client.get("https://example.com/api")
            
        assert response.status_code == 200
        assert response.json() == {"data": "mocked response"}
```

## 부하 테스트 도구

### locust

[locust](https://locust.io/)는 성능 및 부하 테스트에 사용됩니다.

#### 설치

```bash
pip install locust
```

#### 기본 사용법

```python
# locustfile.py
from locust import HttpUser, task, between

class WebsiteUser(HttpUser):
    wait_time = between(1, 3)  # 요청 사이에 1-3초 대기
    
    @task
    def index_page(self):
        self.client.get("/")
        
    @task(3)  # 가중치 3배
    def view_items(self):
        self.client.get("/items")
        
    @task(2)
    def create_item(self):
        self.client.post("/items/", json={
            "name": "Test Item",
            "price": 19.99
        })
```

실행:

```bash
locust -f locustfile.py
```

## 테스트 데이터 생성 도구

### Faker

[Faker](https://faker.readthedocs.io/)는 테스트용 가짜 데이터를 생성하는 데 사용됩니다.

#### 설치

```bash
pip install Faker
```

#### 기본 사용법

```python
from faker import Faker

# 기본 Faker 인스턴스 생성
fake = Faker()

# 한국어 데이터 생성을 위한 설정
fake_kr = Faker('ko_KR')

def generate_user_data(count=1):
    users = []
    for _ in range(count):
        users.append({
            "name": fake_kr.name(),
            "email": fake.email(),
            "address": fake_kr.address(),
            "phone": fake_kr.phone_number(),
            "job": fake_kr.job(),
            "company": fake_kr.company()
        })
    return users

# 테스트에서 사용
def test_user_list():
    # 10명의 테스트 사용자 데이터 생성
    test_users = generate_user_data(10)
    # 테스트 로직...
```

## 디버깅 도구

### pytest-pdb

[pytest-pdb](https://github.com/finklabs/pytest-pdb)는 테스트 실패 시 자동으로 디버거를 시작하는 플러그인입니다.

#### 설치

```bash
pip install pytest-pdb
```

#### 기본 사용법

```bash
# 실패한 테스트에서 디버거 실행
pytest --pdb

# 첫 번째 실패 시 디버거 실행 후 종료
pytest --pdb --exitfirst
```

### pytest-xdist

[pytest-xdist](https://pytest-xdist.readthedocs.io/)는 테스트를 병렬로 실행하는 플러그인입니다.

#### 설치

```bash
pip install pytest-xdist
```

#### 기본 사용법

```bash
# 4개의 프로세스로 병렬 실행
pytest -n 4

# CPU 코어 수만큼 프로세스 사용
pytest -n auto
```

## 테스트 보고서 도구

### pytest-html

[pytest-html](https://pytest-html.readthedocs.io/)은 HTML 형식의 테스트 보고서를 생성하는 플러그인입니다.

#### 설치

```bash
pip install pytest-html
```

#### 기본 사용법

```bash
# HTML 보고서 생성
pytest --html=report.html
```

### pytest-json-report

[pytest-json-report](https://github.com/numirias/pytest-json-report)는 JSON 형식의 테스트 보고서를 생성하는 플러그인입니다.

#### 설치

```bash
pip install pytest-json-report
```

#### 기본 사용법

```bash
# JSON 보고서 생성
pytest --json-report

# 보고서 파일 지정
pytest --json-report --json-report-file=report.json
```
