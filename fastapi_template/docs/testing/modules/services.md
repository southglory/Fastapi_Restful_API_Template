# Services 모듈 테스트 가이드

## 개요

`services` 모듈은 애플리케이션의 비즈니스 로직을 구현하는 계층으로, API 엔드포인트와 데이터 액세스 계층 사이의 중간 계층 역할을 합니다. 이 모듈은 데이터 변환, 비즈니스 규칙 적용, 외부 서비스 통합, 도메인 로직 구현 등의 책임을 가집니다.

## 테스트 용이성

- **난이도**: 중간
- **이유**:
  - 외부 의존성(데이터베이스, 외부 API 등)을 모킹해야 함
  - 복잡한 비즈니스 로직 테스트가 필요함
  - 다양한 시나리오와 에지 케이스 처리 필요
  - 비동기 코드 테스트가 필요한 경우가 많음

## 테스트 대상

주요 테스트 대상은 다음과 같습니다:

1. **데이터 변환 로직**
   - 모델간 변환 (예: DB 모델 → API 응답 모델)
   - 데이터 정제 및 가공
   - 형식 변환

2. **비즈니스 규칙 적용**
   - 유효성 검증 로직
   - 조건부 처리
   - 계산 및 집계 로직

3. **외부 서비스 통합**
   - API 클라이언트 호출
   - 타사 라이브러리 사용
   - 외부 시스템과의 통신

4. **트랜잭션 관리**
   - 원자적 작업 보장
   - 롤백 처리
   - 일관성 유지

## 테스트 접근법

Services 모듈 테스트 시 다음 접근법을 권장합니다:

1. **단위 테스트**: 개별 서비스 메서드 테스트 (의존성 모킹)
2. **통합 테스트**: 서비스 간 상호작용 테스트
3. **모의 테스트**: 외부 의존성 모킹을 통한 테스트
4. **파라미터화 테스트**: 다양한 입력 데이터로 같은 함수 테스트

## 테스트 예시

### 사용자 서비스 테스트

```python
# tests/test_services/test_user_service.py
import pytest
from unittest.mock import patch, MagicMock, AsyncMock
from app.common.services.user_service import UserService
from app.common.schemas.user import UserCreate, UserResponse
from app.common.exceptions import NotFoundException, ValidationException

@pytest.fixture
def user_service():
    # 테스트용 사용자 서비스 인스턴스 생성
    return UserService()

@pytest.mark.asyncio
async def test_get_user_by_id_success(user_service):
    # 사용자 조회 성공 테스트
    user_id = 1
    mock_user = {"id": user_id, "username": "testuser", "email": "test@example.com"}
    
    # 데이터베이스 리포지토리 모킹
    with patch("app.common.services.user_service.UserRepository") as mock_repo:
        # 모의 리포지토리 설정
        mock_repo_instance = AsyncMock()
        mock_repo.return_value = mock_repo_instance
        mock_repo_instance.get_by_id.return_value = mock_user
        
        # 테스트할 메서드 호출
        result = await user_service.get_user_by_id(user_id)
        
        # 결과 확인
        assert result["id"] == user_id
        assert result["username"] == "testuser"
        # 비밀번호와 같은 민감한 정보는 제외되어야 함
        assert "password" not in result
        
        # 리포지토리 메서드가 올바른 인자로 호출되었는지 확인
        mock_repo_instance.get_by_id.assert_called_once_with(user_id)

@pytest.mark.asyncio
async def test_get_user_by_id_not_found(user_service):
    # 사용자 조회 실패 테스트
    user_id = 999
    
    # 데이터베이스 리포지토리 모킹
    with patch("app.common.services.user_service.UserRepository") as mock_repo:
        # 모의 리포지토리 설정 - 사용자 없음
        mock_repo_instance = AsyncMock()
        mock_repo.return_value = mock_repo_instance
        mock_repo_instance.get_by_id.return_value = None
        
        # 예외가 발생하는지 확인
        with pytest.raises(NotFoundException) as exc_info:
            await user_service.get_user_by_id(user_id)
        
        # 예외 메시지 확인
        assert f"User with ID {user_id} not found" in str(exc_info.value)
        
        # 리포지토리 메서드가 올바른 인자로 호출되었는지 확인
        mock_repo_instance.get_by_id.assert_called_once_with(user_id)

@pytest.mark.asyncio
async def test_create_user_success(user_service):
    # 사용자 생성 성공 테스트
    user_data = UserCreate(
        username="newuser",
        email="new@example.com",
        password="securepassword"
    )
    
    created_user = {
        "id": 1,
        "username": user_data.username,
        "email": user_data.email,
        "is_active": True
    }
    
    # 모킹 설정
    with patch("app.common.services.user_service.UserRepository") as mock_repo, \
         patch("app.common.services.user_service.hash_password") as mock_hash:
        
        # 비밀번호 해싱 모킹
        mock_hash.return_value = "hashed_password"
        
        # 리포지토리 모킹
        mock_repo_instance = AsyncMock()
        mock_repo.return_value = mock_repo_instance
        mock_repo_instance.create.return_value = created_user
        mock_repo_instance.get_by_email.return_value = None  # 이메일 중복 체크
        
        # 테스트할 메서드 호출
        result = await user_service.create_user(user_data)
        
        # 결과 확인
        assert result["id"] == 1
        assert result["username"] == user_data.username
        assert result["email"] == user_data.email
        assert "password" not in result
        
        # 비밀번호 해싱 호출 확인
        mock_hash.assert_called_once_with(user_data.password)
        
        # 이메일 중복 체크 확인
        mock_repo_instance.get_by_email.assert_called_once_with(user_data.email)
        
        # 사용자 생성 호출 확인
        mock_repo_instance.create.assert_called_once()
        # 해시된 비밀번호가 사용되었는지 확인
        create_call_args = mock_repo_instance.create.call_args[0][0]
        assert create_call_args["password"] == "hashed_password"

@pytest.mark.asyncio
async def test_create_user_duplicate_email(user_service):
    # 이메일 중복으로 인한 사용자 생성 실패 테스트
    user_data = UserCreate(
        username="duplicateuser",
        email="existing@example.com",
        password="securepassword"
    )
    
    existing_user = {
        "id": 2,
        "username": "existinguser",
        "email": user_data.email
    }
    
    # 모킹 설정
    with patch("app.common.services.user_service.UserRepository") as mock_repo:
        # 리포지토리 모킹 - 이미 존재하는 이메일
        mock_repo_instance = AsyncMock()
        mock_repo.return_value = mock_repo_instance
        mock_repo_instance.get_by_email.return_value = existing_user
        
        # 예외가 발생하는지 확인
        with pytest.raises(ValidationException) as exc_info:
            await user_service.create_user(user_data)
        
        # 예외 메시지 확인
        assert f"User with email {user_data.email} already exists" in str(exc_info.value)
        
        # 이메일 중복 체크만 호출되고 생성은 호출되지 않았는지 확인
        mock_repo_instance.get_by_email.assert_called_once_with(user_data.email)
        mock_repo_instance.create.assert_not_called()
```

### 상품 서비스 테스트

```python
# tests/test_services/test_product_service.py
import pytest
from unittest.mock import patch, AsyncMock
from datetime import datetime
from app.common.services.product_service import ProductService
from app.common.schemas.product import ProductCreate, ProductUpdate
from app.common.exceptions import NotFoundException, ValidationException

@pytest.fixture
def product_service():
    # 테스트용 상품 서비스 인스턴스 생성
    return ProductService()

@pytest.mark.asyncio
async def test_get_products_with_filters(product_service):
    # 필터를 적용한 상품 목록 조회 테스트
    filters = {
        "category": "electronics",
        "min_price": 50,
        "max_price": 500,
        "in_stock": True
    }
    
    mock_products = [
        {"id": 1, "name": "Product 1", "price": 100, "category": "electronics", "in_stock": True},
        {"id": 2, "name": "Product 2", "price": 200, "category": "electronics", "in_stock": True}
    ]
    
    # 리포지토리 모킹
    with patch("app.common.services.product_service.ProductRepository") as mock_repo:
        mock_repo_instance = AsyncMock()
        mock_repo.return_value = mock_repo_instance
        mock_repo_instance.get_all_with_filters.return_value = mock_products
        
        # 테스트할 메서드 호출
        result = await product_service.get_products(
            category=filters["category"],
            min_price=filters["min_price"],
            max_price=filters["max_price"],
            in_stock=filters["in_stock"]
        )
        
        # 결과 확인
        assert len(result) == 2
        assert result[0]["id"] == 1
        assert result[1]["id"] == 2
        assert all(p["category"] == "electronics" for p in result)
        assert all(p["in_stock"] for p in result)
        assert all(50 <= p["price"] <= 500 for p in result)
        
        # 리포지토리 호출 확인
        mock_repo_instance.get_all_with_filters.assert_called_once()
        # 필터 파라미터 확인
        call_kwargs = mock_repo_instance.get_all_with_filters.call_args[1]
        assert call_kwargs["category"] == filters["category"]
        assert call_kwargs["min_price"] == filters["min_price"]
        assert call_kwargs["max_price"] == filters["max_price"]
        assert call_kwargs["in_stock"] == filters["in_stock"]

@pytest.mark.asyncio
async def test_update_product_partial(product_service):
    # 상품 부분 업데이트 테스트
    product_id = 1
    update_data = ProductUpdate(
        price=150,
        discount_percent=10
    )
    
    existing_product = {
        "id": product_id,
        "name": "Original Product",
        "description": "Original description",
        "price": 100,
        "category": "electronics",
        "in_stock": True,
        "discount_percent": 0,
        "updated_at": datetime(2023, 1, 1)
    }
    
    updated_product = {
        **existing_product,
        "price": update_data.price,
        "discount_percent": update_data.discount_percent,
        "updated_at": datetime(2023, 1, 2)
    }
    
    # 리포지토리 모킹
    with patch("app.common.services.product_service.ProductRepository") as mock_repo:
        mock_repo_instance = AsyncMock()
        mock_repo.return_value = mock_repo_instance
        mock_repo_instance.get_by_id.return_value = existing_product
        mock_repo_instance.update.return_value = updated_product
        
        # 테스트할 메서드 호출
        result = await product_service.update_product(product_id, update_data)
        
        # 결과 확인
        assert result["id"] == product_id
        assert result["price"] == update_data.price
        assert result["discount_percent"] == update_data.discount_percent
        # 업데이트하지 않은 필드는 그대로 유지
        assert result["name"] == existing_product["name"]
        assert result["description"] == existing_product["description"]
        assert result["category"] == existing_product["category"]
        
        # 리포지토리 호출 확인
        mock_repo_instance.get_by_id.assert_called_once_with(product_id)
        mock_repo_instance.update.assert_called_once()
        # 부분 업데이트만 적용되었는지 확인
        update_call_args = mock_repo_instance.update.call_args[0]
        assert update_call_args[0] == product_id
        assert "price" in update_call_args[1]
        assert "discount_percent" in update_call_args[1]
        assert "name" not in update_call_args[1]
        assert "description" not in update_call_args[1]

@pytest.mark.asyncio
async def test_process_order_success(product_service):
    # 주문 처리 성공 테스트 (트랜잭션 테스트)
    order_data = {
        "user_id": 1,
        "items": [
            {"product_id": 1, "quantity": 2},
            {"product_id": 2, "quantity": 1}
        ],
        "shipping_address": "123 Test St",
        "payment_method": "credit_card"
    }
    
    product1 = {"id": 1, "name": "Product 1", "price": 100, "stock_count": 10}
    product2 = {"id": 2, "name": "Product 2", "price": 200, "stock_count": 5}
    
    # 모킹 설정
    with patch("app.common.services.product_service.ProductRepository") as mock_product_repo, \
         patch("app.common.services.product_service.OrderRepository") as mock_order_repo, \
         patch("app.common.services.product_service.get_db_transaction") as mock_get_tx:
        
        # 트랜잭션 모킹
        mock_db = AsyncMock()
        
        async def mock_tx_gen():
            yield mock_db
        
        mock_get_tx.return_value = mock_tx_gen()
        
        # 상품 리포지토리 모킹
        mock_product_repo_instance = AsyncMock()
        mock_product_repo.return_value = mock_product_repo_instance
        mock_product_repo_instance.get_by_id.side_effect = [product1, product2]
        
        # 주문 리포지토리 모킹
        mock_order_repo_instance = AsyncMock()
        mock_order_repo.return_value = mock_order_repo_instance
        mock_order_repo_instance.create.return_value = {"id": 1, **order_data}
        
        # 테스트할 메서드 호출
        result = await product_service.process_order(order_data)
        
        # 결과 확인
        assert result["id"] == 1
        assert result["user_id"] == order_data["user_id"]
        assert len(result["items"]) == len(order_data["items"])
        
        # 각 상품의 재고가 차감되었는지 확인
        update_calls = mock_product_repo_instance.update.call_args_list
        assert len(update_calls) == 2
        
        # 첫 번째 상품 업데이트 확인 (10 - 2 = 8)
        assert update_calls[0][0][0] == 1  # product_id
        assert update_calls[0][0][1]["stock_count"] == 8
        
        # 두 번째 상품 업데이트 확인 (5 - 1 = 4)
        assert update_calls[1][0][0] == 2  # product_id
        assert update_calls[1][0][1]["stock_count"] == 4
        
        # 트랜잭션 커밋 확인
        assert mock_db.commit.called
```

### 외부 API 클라이언트 서비스 테스트

```python
# tests/test_services/test_external_api_service.py
import pytest
from unittest.mock import patch, AsyncMock
import aiohttp
from app.common.services.external_api_service import ExternalAPIService
from app.common.exceptions import ExternalAPIException

@pytest.fixture
def api_service():
    # 테스트용 외부 API 서비스 인스턴스 생성
    return ExternalAPIService(base_url="https://api.example.com")

@pytest.mark.asyncio
async def test_get_external_data_success(api_service):
    # 외부 API 데이터 조회 성공 테스트
    mock_response_data = {
        "id": 123,
        "name": "External Resource",
        "status": "active"
    }
    
    # aiohttp ClientSession 모킹
    with patch("aiohttp.ClientSession.get") as mock_get:
        # 모의 응답 설정
        mock_response = AsyncMock()
        mock_response.status = 200
        mock_response.json.return_value = mock_response_data
        mock_get.return_value.__aenter__.return_value = mock_response
        
        # 테스트할 메서드 호출
        result = await api_service.get_data("/resources/123")
        
        # 결과 확인
        assert result == mock_response_data
        
        # API 호출 확인
        mock_get.assert_called_once()
        # 호출 URL 확인
        call_args = mock_get.call_args[0]
        assert call_args[0] == "https://api.example.com/resources/123"

@pytest.mark.asyncio
async def test_get_external_data_error(api_service):
    # 외부 API 오류 처리 테스트
    # aiohttp ClientSession 모킹
    with patch("aiohttp.ClientSession.get") as mock_get:
        # 모의 오류 응답 설정
        mock_response = AsyncMock()
        mock_response.status = 404
        mock_response.json.return_value = {"error": "Resource not found"}
        mock_response.text.return_value = "Not Found"
        mock_get.return_value.__aenter__.return_value = mock_response
        
        # 예외가 발생하는지 확인
        with pytest.raises(ExternalAPIException) as exc_info:
            await api_service.get_data("/resources/999")
        
        # 예외 메시지 확인
        assert "API request failed with status 404" in str(exc_info.value)
        
        # API 호출 확인
        mock_get.assert_called_once()

@pytest.mark.asyncio
async def test_post_data_to_external_api(api_service):
    # 외부 API에 데이터 전송 테스트
    request_data = {
        "name": "New Resource",
        "type": "test"
    }
    
    mock_response_data = {
        "id": 456,
        "name": "New Resource",
        "type": "test",
        "created_at": "2023-01-01T12:00:00Z"
    }
    
    # aiohttp ClientSession 모킹
    with patch("aiohttp.ClientSession.post") as mock_post:
        # 모의 응답 설정
        mock_response = AsyncMock()
        mock_response.status = 201
        mock_response.json.return_value = mock_response_data
        mock_post.return_value.__aenter__.return_value = mock_response
        
        # 테스트할 메서드 호출
        result = await api_service.create_data("/resources", request_data)
        
        # 결과 확인
        assert result == mock_response_data
        assert result["id"] == 456
        
        # API 호출 확인
        mock_post.assert_called_once()
        # 호출 URL 및 데이터 확인
        call_args, call_kwargs = mock_post.call_args
        assert call_args[0] == "https://api.example.com/resources"
        assert call_kwargs["json"] == request_data
        assert call_kwargs["headers"]["Content-Type"] == "application/json"

@pytest.mark.asyncio
async def test_external_api_connection_error(api_service):
    # 네트워크 연결 오류 테스트
    # aiohttp ClientSession 모킹
    with patch("aiohttp.ClientSession.get") as mock_get:
        # 연결 오류 시뮬레이션
        mock_get.side_effect = aiohttp.ClientConnectionError("Connection refused")
        
        # 예외가 발생하는지 확인
        with pytest.raises(ExternalAPIException) as exc_info:
            await api_service.get_data("/resources/123")
        
        # 예외 메시지 확인
        assert "Failed to connect to external API" in str(exc_info.value)
        
        # API 호출 확인
        mock_get.assert_called_once()
```

## 모킹 전략

[공통 테스트 패턴](../common_test_patterns.md)의 모킹 전략을 참조하세요. Service 모듈에 특화된 모킹 전략은 다음과 같습니다:

1. **리포지토리 모킹**: 데이터 액세스 계층(Repository)을 모킹하여 데이터베이스 의존성 제거
2. **외부 서비스 모킹**: API 클라이언트, 메시징 시스템 등 외부 서비스 호출 모킹
3. **컨텍스트 관리자 모킹**: 트랜잭션, 캐시 등의 컨텍스트 관리자 동작 모킹
4. **다른 서비스 모킹**: 서비스 간 의존성이 있는 경우 다른 서비스 모킹

## 테스트 커버리지 확인

Service 모듈의 테스트 커버리지를 확인하세요:

```bash
pytest --cov=app.services tests/test_services/
```

## 모범 사례

[공통 테스트 패턴](../common_test_patterns.md)의 모범 사례와 함께 Service 모듈에 특화된 모범 사례는 다음과 같습니다:

1. **비즈니스 규칙 검증**: 모든 비즈니스 규칙이 올바르게 적용되는지 확인
2. **예외 처리 테스트**: 하위 계층(리포지토리 등)에서 발생하는 예외가 적절히 처리되는지 확인
3. **시나리오 기반 테스트**: 실제 사용 시나리오를 기반으로 여러 서비스 메서드 연계 테스트
4. **경계값 검증**: 임계치, 최소/최대값 등의 경계값 케이스에 대한 테스트

## 주의사항

[공통 테스트 패턴](../common_test_patterns.md)의 주의사항과 함께 Service 모듈 테스트 시 추가로 고려해야 할 사항:

1. **순환 의존성**: 서비스 간 순환 의존성이 있는 경우 적절한 모킹 전략 사용
2. **트랜잭션 관리**: 여러 리포지토리 호출을 포함하는 서비스 메서드의 트랜잭션 처리 테스트
3. **비동기 처리**: 비동기 서비스 메서드의 정확한 테스트를 위한 `pytest-asyncio` 사용
4. **상태 관리**: 서비스가 상태를 유지하는 경우 테스트 간 상태 격리 보장
