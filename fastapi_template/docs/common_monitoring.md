# 공통 모니터링 모듈 상세 가이드

이 문서는 FastAPI 템플릿의 공통 모니터링 모듈에 대한 상세 사용법과 설명을 제공합니다.

## 목차

- [상태 모니터링](#상태-모니터링)
- [메트릭 수집](#메트릭-수집)
- [로깅 시스템](#로깅-시스템)
- [트레이싱](#트레이싱)
- [알림 시스템](#알림-시스템)

## 상태 모니터링

`app.common.monitoring.health` 모듈은 애플리케이션 상태 확인을 위한 엔드포인트와 유틸리티를 제공합니다.

### 상태 확인 엔드포인트

```python
from fastapi import FastAPI
from app.common.monitoring.health import setup_health_endpoint

app = FastAPI()

# 기본 상태 확인 엔드포인트 설정
setup_health_endpoint(app)

# 커스텀 상태 확인 엔드포인트 설정
setup_health_endpoint(
    app,
    path="/status",
    tags=["status"],
    include_details=True,  # 상세 정보 포함
    expose_metrics=True    # 메트릭 정보 포함
)
```

### 상태 체크 커스터마이징

```python
from fastapi import FastAPI
from app.common.monitoring.health import (
    setup_health_endpoint,
    register_health_check
)

app = FastAPI()
setup_health_endpoint(app)

# 데이터베이스 상태 확인 등록
@register_health_check("database")
async def check_database():
    try:
        # 데이터베이스 연결 확인
        await db.execute("SELECT 1")
        return True, "데이터베이스 연결 정상"
    except Exception as e:
        return False, f"데이터베이스 연결 실패: {str(e)}"

# Redis 상태 확인 등록
@register_health_check("redis")
async def check_redis():
    try:
        # Redis 연결 확인
        redis = await get_redis_connection()
        await redis.ping()
        return True, "Redis 연결 정상"
    except Exception as e:
        return False, f"Redis 연결 실패: {str(e)}"
```

## 메트릭 수집

`app.common.monitoring.metrics` 모듈은 애플리케이션 성능 메트릭을 수집하고 제공합니다.

### 메트릭 엔드포인트 설정

```python
from fastapi import FastAPI
from app.common.monitoring.metrics import setup_metrics

app = FastAPI()

# 메트릭 설정 (Prometheus 형식)
setup_metrics(app)
```

### 커스텀 메트릭 추가

```python
from fastapi import FastAPI
from app.common.monitoring.metrics import (
    create_counter,
    create_gauge,
    create_histogram
)

app = FastAPI()

# 카운터 메트릭 생성
api_requests = create_counter(
    name="api_requests_total",
    description="API 요청 총 개수",
    labels=["method", "endpoint", "status"]
)

# 게이지 메트릭 생성
active_users = create_gauge(
    name="active_users",
    description="현재 활성 사용자 수"
)

# 히스토그램 메트릭 생성
request_duration = create_histogram(
    name="request_duration_seconds",
    description="요청 처리 시간 분포",
    buckets=[0.1, 0.25, 0.5, 1.0, 2.5, 5.0]
)

# API에서 메트릭 사용
@app.get("/users")
async def get_users():
    # 요청 카운터 증가
    api_requests.inc(labels={"method": "GET", "endpoint": "/users", "status": "200"})
    
    start_time = time.time()
    result = await fetch_users()
    elapsed = time.time() - start_time
    
    # 요청 처리 시간 기록
    request_duration.observe(elapsed)
    
    return result
```

## 로깅 시스템

`app.common.monitoring.logging` 모듈은 구조화된 로깅 시스템을 제공합니다.

### 로거 설정

```python
from fastapi import FastAPI
from app.common.monitoring.logging import setup_logging, get_logger

# 애플리케이션 로깅 설정
setup_logging(
    log_level="INFO",
    json_format=True,  # JSON 형식으로 로깅
    log_to_file=True,  # 파일에 로깅
    log_file="app.log"
)

# 모듈별 로거 가져오기
logger = get_logger("api.users")
logger.info("사용자 모듈 초기화 완료")
```

### 구조화된 로깅

```python
from app.common.monitoring.logging import get_logger

logger = get_logger("api.orders")

# 컨텍스트 정보와 함께 로깅
logger.info("주문 생성 완료", extra={
    "order_id": order.id,
    "user_id": user.id,
    "total_amount": order.total_amount,
    "items_count": len(order.items)
})

# 오류 로깅
try:
    process_payment(order)
except Exception as e:
    logger.error("결제 처리 실패", exc_info=True, extra={
        "order_id": order.id,
        "payment_method": order.payment_method
    })
```

## 트레이싱

`app.common.monitoring.tracing` 모듈은 분산 트레이싱 기능을 제공합니다.

### 트레이싱 설정

```python
from fastapi import FastAPI
from app.common.monitoring.tracing import setup_tracing

app = FastAPI()

# OpenTelemetry 트레이싱 설정
setup_tracing(
    app,
    service_name="fastapi-app",
    jaeger_host="jaeger",
    jaeger_port=6831
)
```

### 스팬 생성 및 추적

```python
from fastapi import APIRouter, Depends
from app.common.monitoring.tracing import tracer, create_span

router = APIRouter()

@router.get("/orders/{order_id}")
async def get_order(order_id: int):
    # 현재 스팬 가져오기
    with tracer.start_as_current_span("get_order") as span:
        # 스팬에 속성 추가
        span.set_attribute("order_id", order_id)
        
        # 데이터베이스 조회
        with create_span("db.query", parent=span) as db_span:
            order = await db.get_order(order_id)
            db_span.set_attribute("db.query.result_size", 1)
        
        # 관련 정보 조회
        with create_span("service.call", parent=span) as service_span:
            user = await user_service.get_user(order.user_id)
            service_span.set_attribute("service.name", "user_service")
        
        return {"order": order, "user": user}
```

## 알림 시스템

`app.common.monitoring.alerts` 모듈은 중요한 이벤트에 대한 알림 기능을 제공합니다.

### 알림 설정

```python
from app.common.monitoring.alerts import setup_alerts, send_alert

# 알림 채널 설정
setup_alerts(
    slack_webhook_url="https://hooks.slack.com/services/...",
    email_config={
        "host": "smtp.example.com",
        "port": 587,
        "username": "alerts@example.com",
        "password": "password",
        "recipients": ["admin@example.com"]
    }
)
```

### 알림 전송

```python
from app.common.monitoring.alerts import send_alert, AlertLevel

# 심각도에 따른 알림 전송
try:
    perform_critical_operation()
except Exception as e:
    # 긴급 알림 전송
    send_alert(
        level=AlertLevel.CRITICAL,
        title="결제 시스템 장애",
        message=f"결제 처리 중 오류 발생: {str(e)}",
        details={
            "error_type": type(e).__name__,
            "timestamp": datetime.now().isoformat(),
            "affected_service": "payment_processor"
        },
        channels=["slack", "email"]  # 특정 채널로만 전송
    )
```

### 정기 알림 설정

```python
from app.common.monitoring.alerts import schedule_alert

# 일일 리포트 알림 스케줄링
@schedule_alert(cron="0 9 * * *")  # 매일 오전 9시
async def daily_report():
    # 일일 통계 수집
    stats = await collect_daily_stats()
    
    # 알림 내용 작성
    title = f"일일 서비스 리포트 ({datetime.now().date()})"
    message = f"총 요청: {stats['total_requests']}, 오류율: {stats['error_rate']:.2f}%"
    
    return {
        "title": title,
        "message": message,
        "details": stats,
        "level": AlertLevel.INFO,
        "channels": ["slack"]
    }
```
