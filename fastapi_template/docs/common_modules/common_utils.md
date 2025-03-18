# 공통 유틸리티 모듈 상세 가이드

이 문서는 FastAPI 템플릿의 공통 유틸리티 모듈에 대한 상세 사용법과 설명을 제공합니다.

## 목차

- [파일 유틸리티](#파일-유틸리티)
- [날짜 유틸리티](#날짜-유틸리티)
- [문자열 유틸리티](#문자열-유틸리티)
- [로깅 유틸리티](#로깅-유틸리티)
- [비동기 유틸리티](#비동기-유틸리티)

## 파일 유틸리티

`app.common.utils.file_utils` 모듈은 파일 처리를 위한 다양한 함수를 제공합니다.

### 파일 업로드

```python
from app.common.utils.file_utils import save_upload_file, get_file_path

# 파일 저장
file_info = await save_upload_file(
    file=form_file,
    destination="uploads/images",
    filename_prefix="user_",
    allowed_extensions=[".jpg", ".png", ".gif"]
)

# 저장된 파일 경로 가져오기
file_path = get_file_path(file_info["filename"], "uploads/images")
```

### 임시 파일 생성

```python
from app.common.utils.file_utils import create_temp_file, cleanup_temp_files

# 임시 파일 생성
temp_file_path = await create_temp_file(content=b"file content", suffix=".txt")

# 작업 완료 후 정리
await cleanup_temp_files()
```

## 날짜 유틸리티

`app.common.utils.date_utils` 모듈은 날짜와 시간 처리를 위한 함수를 제공합니다.

### 날짜 포맷팅

```python
from app.common.utils.date_utils import format_date, parse_date
from datetime import datetime

# 날짜 포맷팅
now = datetime.now()
formatted = format_date(now, format_str="YYYY-MM-DD HH:mm:ss")

# 문자열에서 날짜 파싱
date_obj = parse_date("2023-01-15", format_str="YYYY-MM-DD")
```

### 상대적 시간 표시

```python
from app.common.utils.date_utils import get_time_ago
from datetime import datetime, timedelta

# 일주일 전 날짜
week_ago = datetime.now() - timedelta(days=7)

# 상대적 시간으로 표시
time_ago = get_time_ago(week_ago)  # "7일 전"
```

## 문자열 유틸리티

`app.common.utils.string_utils` 모듈은 문자열 처리를 위한 유틸리티 함수를 제공합니다.

### 문자열 변환

```python
from app.common.utils.string_utils import to_snake_case, to_camel_case

# 스네이크 케이스 변환
snake = to_snake_case("HelloWorld")  # "hello_world"

# 카멜 케이스 변환
camel = to_camel_case("hello_world")  # "helloWorld"
```

### 랜덤 문자열 생성

```python
from app.common.utils.string_utils import generate_random_string, generate_slug

# 랜덤 문자열 생성
random_str = generate_random_string(length=10)  # "a1b2c3d4e5"

# 슬러그 생성
slug = generate_slug("Hello World!")  # "hello-world"
```

## 로깅 유틸리티

`app.common.utils.logging_utils` 모듈은 로깅 관련 유틸리티를 제공합니다.

### 로거 설정

```python
from app.common.utils.logging_utils import get_logger, setup_logging

# 로깅 설정
setup_logging(log_level="INFO", log_to_file=True, log_file="app.log")

# 로거 가져오기
logger = get_logger("my_module")
logger.info("정보 메시지")
logger.error("오류 발생", exc_info=True)
```

### 요청 로깅

```python
from app.common.utils.logging_utils import log_request

# API 요청 로깅
@app.middleware("http")
async def logging_middleware(request: Request, call_next):
    return await log_request(request, call_next)
```

## 비동기 유틸리티

`app.common.utils.async_utils` 모듈은 비동기 작업을 위한 유틸리티를 제공합니다.

### 병렬 실행

```python
from app.common.utils.async_utils import run_parallel, run_in_threadpool

# 여러 비동기 함수를 병렬로 실행
results = await run_parallel(
    async_function1(arg1),
    async_function2(arg2),
    async_function3(arg3)
)

# CPU 바운드 작업을 스레드 풀에서 실행
result = await run_in_threadpool(cpu_intensive_function, arg1, arg2)
```

### 재시도 메커니즘

```python
from app.common.utils.async_utils import retry

# 실패 시 재시도 로직
@retry(attempts=3, delay=1, backoff=2, exceptions=(ConnectionError,))
async def connect_to_service():
    # 서비스 연결 시도
    return await service.connect()
```

### 백그라운드 작업

```python
from app.common.utils.async_utils import run_background_task

# 백그라운드 작업 실행
@app.post("/send-emails")
async def send_emails(emails: List[str]):
    # 응답은 즉시 반환하고 이메일 전송은 백그라운드에서 처리
    run_background_task(send_emails_async, emails)
    return {"message": "이메일 전송 작업이 백그라운드에서 실행 중입니다"}
```
