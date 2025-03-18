# 유틸리티 모듈 테스트 가이드

이 문서는 `app/common/utils` 디렉토리에 있는 유틸리티 모듈의 효과적인 테스트 방법을 설명합니다.

## 목차

- [개요](#개요)
- [유틸리티 테스트의 중요성](#유틸리티-테스트의-중요성)
- [테스트 패턴](#테스트-패턴)
- [유틸리티 유형별 테스트 전략](#유틸리티-유형별-테스트-전략)
  - [날짜/시간 유틸리티](#날짜시간-유틸리티)
  - [문자열 유틸리티](#문자열-유틸리티)
  - [파일 유틸리티](#파일-유틸리티)
  - [페이지네이션 유틸리티](#페이지네이션-유틸리티)
  - [비동기 유틸리티](#비동기-유틸리티)
- [모킹과 패치](#모킹과-패치)
- [경계값 테스트](#경계값-테스트)
- [예제](#예제)

## 개요

유틸리티 모듈은 애플리케이션 전반에서 사용되는 작은 함수들로 구성되어 있습니다. 이러한 함수들은 단순해 보일 수 있지만, 애플리케이션의 핵심 기능을 지원하기 때문에 철저한 테스트가 필요합니다.

## 유틸리티 테스트의 중요성

유틸리티 함수 테스트는 다음과 같은 이유로 중요합니다:

1. **높은 재사용성**: 유틸리티 함수는 코드베이스 전체에서 사용되므로, 한 곳의 버그가 전체 애플리케이션에 영향을 미칠 수 있습니다.
2. **명확한 입출력**: 작은 유틸리티 함수는 일반적으로 입력과 출력이 명확하게 정의되어 있어 테스트하기 용이합니다.
3. **문서화 역할**: 테스트는 함수 사용법의 좋은 예시가 되어 문서 역할을 합니다.
4. **리팩터링 안전망**: 테스트는 코드 리팩터링 시 안전망 역할을 합니다.

## 테스트 패턴

유틸리티 함수를 테스트할 때 일반적으로 다음 패턴을 따릅니다:

1. **입력 준비(Arrange)**: 테스트에 필요한 입력 데이터 설정
2. **함수 실행(Act)**: 테스트 대상 함수 호출
3. **결과 검증(Assert)**: 예상 결과와 실제 결과 비교

```python
def test_format_datetime():
    # 준비(Arrange)
    dt = datetime(2023, 5, 15, 10, 30, 0)
    expected = "2023-05-15 10:30:00"
    
    # 실행(Act)
    result = format_datetime(dt)
    
    # 검증(Assert)
    assert result == expected
```

## 유틸리티 유형별 테스트 전략

### 날짜/시간 유틸리티

날짜/시간 관련 유틸리티는 다음과 같은 전략으로 테스트합니다:

#### 고정된 날짜 테스트

```python
def test_format_datetime_custom_format():
    dt = datetime(2023, 5, 15, 10, 30, 0)
    assert format_datetime(dt, "%Y/%m/%d") == "2023/05/15"
    assert format_datetime(dt, "%H:%M") == "10:30"
```

#### 현재 시간 테스트

현재 시간을 사용하는 함수는 `freezegun` 라이브러리를 사용하여 시간을 고정할 수 있습니다:

```python
from freezegun import freeze_time

@freeze_time("2023-05-15 10:30:00")
def test_get_utc_now():
    utc_now = get_utc_now()
    assert utc_now.year == 2023
    assert utc_now.month == 5
    assert utc_now.day == 15
```

### 문자열 유틸리티

문자열 유틸리티 함수는 다양한 입력 케이스를 테스트해야 합니다:

```python
def test_to_snake_case():
    # 기본 케이스
    assert to_snake_case("HelloWorld") == "hello_world"
    # 이미 스네이크 케이스인 경우
    assert to_snake_case("hello_world") == "hello_world"
    # 특수 문자가 있는 경우
    assert to_snake_case("Hello-World") == "hello_world"
    # 공백이 있는 경우
    assert to_snake_case("Hello World") == "hello_world"
```

### 파일 유틸리티

파일 관련 유틸리티는 실제 파일 시스템에 의존하므로 임시 디렉토리를 사용하거나 모킹을 활용합니다:

```python
import tempfile
import os

def test_save_upload_file():
    # 임시 디렉토리 생성
    with tempfile.TemporaryDirectory() as temp_dir:
        # 테스트용 파일 데이터
        file_content = b"test content"
        mock_file = Mock(filename="test.txt", content=file_content)
        
        # 함수 실행
        file_info = save_upload_file(
            file=mock_file,
            destination=temp_dir,
            allowed_extensions=[".txt"]
        )
        
        # 결과 검증
        assert os.path.exists(os.path.join(temp_dir, file_info["filename"]))
        with open(os.path.join(temp_dir, file_info["filename"]), "rb") as f:
            assert f.read() == file_content
```

### 페이지네이션 유틸리티

페이지네이션 관련 함수는 다양한 입력 조합과 경계 조건을 테스트합니다:

```python
def test_get_pagination_params():
    # 기본값 테스트
    params = get_pagination_params()
    assert params["page"] == 1
    assert params["size"] == 10
    assert params["skip"] == 0
    
    # 사용자 정의값 테스트
    params = get_pagination_params(page=2, size=20)
    assert params["page"] == 2
    assert params["size"] == 20
    assert params["skip"] == 20
    
    # 경계값 테스트
    params = get_pagination_params(page=0, size=0)
    assert params["page"] == 1  # 최소값으로 조정
    assert params["size"] == 1  # 최소값으로 조정
    
    params = get_pagination_params(size=1000)
    assert params["size"] == 100  # 최대값으로 제한
```

### 비동기 유틸리티

비동기 함수는 `pytest.mark.asyncio` 데코레이터를 사용하여 테스트합니다:

```python
import pytest

@pytest.mark.asyncio
async def test_run_parallel():
    async def async_func1():
        return 1
        
    async def async_func2():
        return 2
    
    results = await run_parallel(async_func1(), async_func2())
    assert results == [1, 2]
```

## 모킹과 패치

외부 의존성이 있는 유틸리티 함수는 `unittest.mock`을 사용하여 테스트합니다:

```python
from unittest.mock import patch, MagicMock

def test_get_service_status():
    with patch('app.common.utils.network.requests.get') as mock_get:
        # Mock 응답 설정
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"status": "healthy"}
        mock_get.return_value = mock_response
        
        # 함수 실행
        status = get_service_status("http://example.com/status")
        
        # 검증
        assert status == "healthy"
        mock_get.assert_called_once_with("http://example.com/status", timeout=5)
```

## 경계값 테스트

유틸리티 함수는 다양한 경계값 케이스를 테스트해야 합니다:

```python
def test_clamp_value():
    # 정상 범위 내 값
    assert clamp_value(5, 0, 10) == 5
    
    # 최소값 경계
    assert clamp_value(0, 0, 10) == 0
    assert clamp_value(-1, 0, 10) == 0
    
    # 최대값 경계
    assert clamp_value(10, 0, 10) == 10
    assert clamp_value(11, 0, 10) == 10
```

## 예제

### datetime.py 테스트

```python
# tests/unit/common/utils/test_datetime.py
import pytest
from datetime import datetime, timedelta
from freezegun import freeze_time
from app.common.utils.datetime import format_datetime, get_utc_now, add_time

class TestDatetimeUtils:
    def test_format_datetime(self):
        # 특정 시간 생성
        dt = datetime(2023, 5, 15, 10, 30, 0)
        # 기본 포맷 테스트
        assert format_datetime(dt) == "2023-05-15 10:30:00"
        # 커스텀 포맷 테스트
        assert format_datetime(dt, "%Y/%m/%d") == "2023/05/15"
        # 다양한 포맷 테스트
        assert format_datetime(dt, "%H:%M") == "10:30"
        assert format_datetime(dt, "%A, %d %B %Y") == "Monday, 15 May 2023"
    
    @freeze_time("2023-05-15 10:30:00")
    def test_get_utc_now(self):
        # 고정된 시간으로 테스트
        utc_now = get_utc_now()
        assert utc_now.year == 2023
        assert utc_now.month == 5
        assert utc_now.day == 15
        assert utc_now.hour == 10
        assert utc_now.minute == 30
        assert utc_now.second == 0
    
    def test_add_time(self):
        dt = datetime(2023, 5, 15, 10, 0, 0)
        # 시간 추가 테스트
        assert add_time(dt, hours=2) == datetime(2023, 5, 15, 12, 0, 0)
        # 일 추가 테스트
        assert add_time(dt, days=3) == datetime(2023, 5, 18, 10, 0, 0)
        # 조합 테스트
        assert add_time(dt, days=1, minutes=30) == datetime(2023, 5, 16, 10, 30, 0)
        # 음수값 테스트
        assert add_time(dt, hours=-5) == datetime(2023, 5, 15, 5, 0, 0)
```

### pagination.py 테스트

```python
# tests/unit/common/utils/test_pagination.py
import pytest
from app.common.utils.pagination import paginate_query, get_pagination_params

class TestPaginationUtils:
    def test_get_pagination_params(self):
        # 기본값 테스트
        params = get_pagination_params()
        assert params["page"] == 1
        assert params["size"] == 10
        assert params["skip"] == 0
        
        # 값 지정 테스트
        params = get_pagination_params(page=2, size=20)
        assert params["page"] == 2
        assert params["size"] == 20
        assert params["skip"] == 20
        
        # 최대값 제한 테스트
        params = get_pagination_params(size=1000)
        assert params["size"] == 100  # 최대값으로 제한
        
        # 최소값 제한 테스트
        params = get_pagination_params(page=0, size=0)
        assert params["page"] == 1  # 최소값으로 조정
        assert params["size"] == 1  # 최소값으로 조정
    
    def test_paginate_query(self):
        # 테스트 데이터
        items = [i for i in range(100)]
        
        # 첫 페이지 테스트
        result = paginate_query(items, page=1, size=10)
        assert len(result["items"]) == 10
        assert result["items"] == items[:10]
        assert result["total"] == 100
        assert result["page"] == 1
        assert result["size"] == 10
        assert result["pages"] == 10
        
        # 마지막 페이지 테스트
        result = paginate_query(items, page=10, size=10)
        assert len(result["items"]) == 10
        assert result["items"] == items[90:100]
        
        # 페이지 범위 초과 테스트
        result = paginate_query(items, page=20, size=10)
        assert len(result["items"]) == 0
        assert result["page"] == 20
        
        # 빈 목록 테스트
        result = paginate_query([], page=1, size=10)
        assert len(result["items"]) == 0
        assert result["total"] == 0
        assert result["pages"] == 0
```
