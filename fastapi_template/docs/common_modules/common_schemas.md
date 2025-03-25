# 스키마 모듈 상세 가이드

이 문서는 FastAPI 템플릿의 스키마 모듈에 대한 상세 사용법과 설명을 제공합니다.

## 목차

- [스키마 분류 체계](#스키마-분류-체계) [@base_schema](/fastapi_template/app/common/schemas/base_schema.py)
- [기본 응답 스키마](#기본-응답-스키마) [@base_schema](/fastapi_template/app/common/schemas/base_schema.py)
- [페이지네이션 스키마](#페이지네이션-스키마) [@pagination_schema](/fastapi_template/app/common/schemas/pagination_schema.py)
- [기본 스키마 클래스](#기본-스키마-클래스) [@base_schema](/fastapi_template/app/common/schemas/base_schema.py)
- [스키마 상속 및 확장](#스키마-상속-및-확장) [@schema_examples](/fastapi_template/app/common/schemas/schema_examples.py)

## 스키마 분류 체계

[@base_schema](/fastapi_template/app/common/schemas/base_schema.py)

스키마는 데이터 흐름 방향과 사용 목적에 따라 체계적으로 분류됩니다. 이를 통해 코드의 가독성과 유지보수성을 향상시킬 수 있습니다.

### 데이터 흐름 방향에 따른 분류

```python
from app.common.schemas.base_schema import InputSchema, OutputSchema, InternalSchema

# 입력 스키마 - 외부에서 시스템으로 들어오는 데이터
class UserInputSchema(InputSchema):
    username: str
    email: str

# 출력 스키마 - 시스템에서 외부로 나가는 데이터
class UserOutputSchema(OutputSchema):
    id: int
    username: str
    email: str
    created_at: datetime

# 내부 스키마 - 시스템 내부에서만 사용되는 데이터
class UserInternalSchema(InternalSchema):
    id: int
    username: str
    email: str
    hashed_password: str  # 내부용 필드
```

### 데이터 생명주기(CRUD)에 따른 분류

```python
from app.common.schemas.base_schema import CreateSchema, ReadSchema, UpdateSchema

# 생성 스키마 (POST 요청)
class UserCreateSchema(CreateSchema):
    username: str
    email: str
    password: str

# 조회 스키마 (GET 응답)
class UserReadSchema(ReadSchema):
    id: int
    username: str
    email: str
    created_at: datetime

# 업데이트 스키마 (PUT/PATCH 요청)
class UserUpdateSchema(UpdateSchema):
    username: Optional[str] = None
    email: Optional[str] = None
```

### 서비스 간 통신을 위한 스키마

```python
from app.common.schemas.base_schema import ServiceSchema, EventSchema

# 서비스 레이어 통신용 스키마
class UserServiceSchema(ServiceSchema):
    id: int
    username: str
    email: str
    hashed_password: str
    is_active: bool
    login_attempts: int

# 이벤트 메시지 스키마
class UserCreatedEvent(EventSchema):
    event_type: str = "user.created"
    payload: Dict[str, Any] = {
        "user_id": int,
        "username": str,
        "email": str
    }
```

### 스키마 분류의 이점

1. **명확한 책임 분리**: 각 스키마가 특정 목적만 담당합니다.
2. **타입 안전성**: 데이터 흐름 경로가 명확해져 타입 에러를 방지합니다.
3. **보안 강화**: 내부 데이터가 외부에 노출되는 것을 방지합니다.
4. **확장성**: 새로운 요구사항에 맞게 스키마를 쉽게 확장할 수 있습니다.
5. **문서화**: API가 요구하는 데이터 구조를 명확하게 표현합니다.

### 스키마 사용 예시

```python
# API 계층
@router.post("/users/", response_model=ResponseSchema[UserReadSchema])
async def create_user(user_data: UserCreateSchema):
    # 서비스 계층 호출
    user_service = UserService()
    new_user = await user_service.create_user(user_data)
    
    # 결과를 API 응답 스키마로 변환
    return ResponseSchema.success(
        data=UserReadSchema.model_validate(new_user),
        message="사용자가 성공적으로 생성되었습니다"
    )
```

자세한 예시는 `app.common.schemas.schema_examples` 모듈을 참조하세요.

자세한 테스트 코드는 [여기](/fastapi_template/tests/test_schemas/)에서 확인할 수 있습니다.

## 기본 응답 스키마

[@base_schema](/fastapi_template/app/common/schemas/base_schema.py)

API 응답을 일관된 형식으로 표현하기 위한 `ResponseSchema` 클래스를 제공합니다.

### 기본 응답 형식

```python
from app.common.schemas.base_schema import ResponseSchema

# 성공 응답
@app.get("/items/{item_id}")
async def get_item(item_id: int):
    item = await get_item_by_id(item_id)
    return ResponseSchema.success(
        data=item,
        message="성공적으로 아이템을 조회했습니다"
    )

# 오류 응답
@app.get("/users/{user_id}")
async def get_user(user_id: int):
    user = await get_user_by_id(user_id)
    if not user:
        return ResponseSchema.error(
            message="사용자를 찾을 수 없습니다",
            code="USER_NOT_FOUND",
            status_code=404
        )
    return ResponseSchema.success(data=user)
```

### 응답 형식

성공 응답:

```json
{
    "success": true,
    "message": "성공적으로 아이템을 조회했습니다",
    "data": {
        "id": 1,
        "name": "아이템 1",
        "price": 10000
    }
}
```

오류 응답:

```json
{
    "success": false,
    "message": "사용자를 찾을 수 없습니다",
    "error_code": "USER_NOT_FOUND",
    "status_code": 404
}
```

## 페이지네이션 스키마

[@pagination_schema](/fastapi_template/app/common/schemas/pagination_schema.py)

페이지네이션 처리를 위한 스키마와 응답 모델을 제공합니다.

### 페이지네이션 파라미터

```python
from app.common.schemas.pagination_schema import PaginationParams

@app.get("/users")
async def get_users(pagination: PaginationParams = Depends()):
    # DB에서 페이지네이션 데이터 조회
    users, total = await get_users_with_pagination(
        skip=pagination.skip,
        limit=pagination.page_size
    )
    
    # pagination.page: 페이지 번호
    # pagination.page_size: 페이지당 아이템 수
    # pagination.skip: 건너뛸 아이템 수 ((page-1) * page_size)
```

### 페이지네이션 응답 모델

```python
from app.common.schemas.pagination_schema import PaginatedResponse, PaginationParams

@app.get("/products")
async def get_products(pagination: PaginationParams = Depends()):
    # 데이터베이스에서 제품 목록과 총 개수 조회
    products, total = await product_service.get_products_paginated(
        skip=pagination.skip,
        limit=pagination.page_size
    )
    
    # 페이지네이션 응답 생성
    return PaginatedResponse.create(
        items=products,
        total_items=total,
        params=pagination
    )
```

### 페이지네이션 요청 및 응답 형식

요청 예시:

```
GET /products?page=2&page_size=10
```

응답 예시:

```json
{
    "items": [
        {"id": 11, "name": "제품 11", "price": 15000},
        {"id": 12, "name": "제품 12", "price": 22000},
        ...
    ],
    "page_info": {
        "page": 2,
        "page_size": 10,
        "total_items": 35,
        "total_pages": 4,
        "has_previous": true,
        "has_next": true
    }
}
```

### 컨트롤러에서의 활용

```python
from app.common.schemas.pagination_schema import PaginationParams, PaginatedResponse
from app.common.utils.pagination import apply_pagination

@router.get("/articles", response_model=PaginatedResponse[ArticleSchema])
async def get_articles(pagination: PaginationParams = Depends()):
    # 쿼리 객체 생성
    query = db.query(Article)
    
    # 필터링 적용
    query = query.filter(Article.is_published == True)
    
    # 페이지네이션 적용
    paginated_query = apply_pagination(query, pagination)
    
    # 데이터 조회
    articles = await paginated_query.all()
    total = await db.query(Article).count()
    
    # 페이지네이션 응답 생성
    return PaginatedResponse.create(
        items=articles, 
        total_items=total, 
        params=pagination
    )
```

## 기본 스키마 클래스

[@base_schema](/fastapi_template/app/common/schemas/base_schema.py)

API 요청 및 응답에 사용되는 기본 스키마 클래스를 제공합니다.

### 기본 모델 스키마

```python
from app.common.schemas.base_schema import BaseSchema
from pydantic import Field
from datetime import datetime

class UserBase(BaseSchema):
    """사용자 기본 스키마"""
    username: str = Field(..., description="사용자 이름")
    email: str = Field(..., description="이메일 주소")
    
class UserCreate(UserBase):
    """사용자 생성 스키마"""
    password: str = Field(..., description="비밀번호")
    
class UserResponse(UserBase):
    """사용자 응답 스키마"""
    id: int = Field(..., description="사용자 ID")
    is_active: bool = Field(True, description="활성화 상태")
    created_at: datetime = Field(..., description="생성 시간")
    updated_at: datetime = Field(..., description="수정 시간")
    
    class Config:
        orm_mode = True
```

### 스키마 사용 예시

```python
@app.post("/users", response_model=ResponseSchema)
async def create_user(user_data: UserCreate):
    # 새 사용자 생성
    new_user = await create_new_user(user_data)
    
    # UserResponse 스키마로 변환하여 반환
    return ResponseSchema.success(
        data=UserResponse.from_orm(new_user),
        message="사용자가 성공적으로 생성되었습니다"
    )
```

## 스키마 상속 및 확장

[@schema_examples](/fastapi_template/app/common/schemas/schema_examples.py)

기본 스키마를 상속하여 새로운 스키마를 정의할 수 있습니다.

### 스키마 상속

```python
from app.common.schemas.base_schema import BaseSchema
from pydantic import Field, validator
from typing import List

# 기본 상품 스키마
class ProductBase(BaseSchema):
    name: str = Field(..., min_length=1, max_length=100)
    description: str = Field(None, max_length=1000)
    price: float = Field(..., gt=0)
    
    @validator('name')
    def name_must_not_contain_special_chars(cls, v):
        if any(char in v for char in ['/', '\\', ':', '*', '?', '"', '<', '>', '|']):
            raise ValueError("상품 이름에 특수 문자를 포함할 수 없습니다")
        return v

# 상품 생성 스키마
class ProductCreate(ProductBase):
    category_id: int = Field(..., gt=0)
    tags: List[str] = Field(default=[])

# 상품 업데이트 스키마 (부분 업데이트 지원)
class ProductUpdate(BaseSchema):
    name: str = Field(None, min_length=1, max_length=100)
    description: str = Field(None, max_length=1000)
    price: float = Field(None, gt=0)
    category_id: int = Field(None, gt=0)
    tags: List[str] = Field(None)

# 상품 응답 스키마
class ProductResponse(ProductBase):
    id: int
    category_id: int
    tags: List[str]
    created_at: datetime
    updated_at: datetime
    
    class Config:
        orm_mode = True
```

### 향후 확장 가능성

스키마 정의를 자동화하고 확장성을 높이기 위한 유틸리티 함수의 추가 개발이 계획되어 있습니다. 이를 통해 스키마 작성의 중복을 줄이고 일관성을 유지할 수 있습니다.
