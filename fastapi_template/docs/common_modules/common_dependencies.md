# FastAPI 의존성 모듈

이 문서는 FastAPI 템플릿의 의존성 주입 모듈(`app/common/dependencies/`)에 대해 설명합니다.

## 목차

- [개요](#개요)
- [인증 의존성](#인증-의존성)
- [데이터베이스 의존성](#데이터베이스-의존성)
- [권한 의존성](#권한-의존성)
- [페이지네이션 의존성](#페이지네이션-의존성)
- [사용 예시](#사용-예시)

## 개요

의존성 주입 모듈은 FastAPI 의존성 주입 시스템을 사용하여 라우트 함수에 필요한 종속성을 제공합니다. 이 모듈은 재사용 가능한 의존성 함수를 정의하여 코드 중복을 줄이고 일관된 방식으로 의존성을 관리할 수 있게 합니다.

## 인증 의존성

[@auth](/fastapi_template/app/common/dependencies/auth.py)

### 현재 사용자 가져오기

```python
from app.common.dependencies.auth import get_current_user

@app.get("/me")
async def get_me(current_user = Depends(get_current_user)):
    return current_user
```

### 활성 사용자 가져오기

비활성화된 사용자를 필터링합니다.

```python
from app.common.dependencies.auth import get_current_active_user

@app.get("/active-user")
async def get_active_user(current_user = Depends(get_current_active_user)):
    return current_user
```

### 관리자 사용자 가져오기

관리자 권한이 있는 사용자만 접근 가능합니다.

```python
from app.common.dependencies.auth import get_current_admin_user

@app.get("/admin-only", dependencies=[Depends(get_current_admin_user)])
async def admin_only():
    return {"message": "관리자만 볼 수 있는 정보"}
```

## 데이터베이스 의존성

[@database](/fastapi_template/app/common/dependencies/database.py)

### 데이터베이스 세션 가져오기

```python
from app.common.dependencies.database import get_db

@app.get("/items")
async def get_items(db = Depends(get_db)):
    return db.query(Item).all()
```

### 트랜잭션 의존성

트랜잭션 내에서 작업을 수행합니다.

```python
from app.common.dependencies.database import get_transaction_session

@app.post("/items")
async def create_item(item_data: ItemCreate, db = Depends(get_transaction_session)):
    try:
        item = Item(**item_data.dict())
        db.add(item)
        db.flush()
        # 추가 작업...
        db.commit()
        return item
    except Exception as e:
        db.rollback()
        raise e
```

## 권한 의존성

[@permissions](/fastapi_template/app/common/dependencies/permissions.py)

### 리소스 소유자 확인

사용자가 리소스의 소유자인지 확인합니다.

```python
from app.common.dependencies.permissions import check_resource_owner

@app.put("/items/{item_id}")
async def update_item(
    item_id: int, 
    item_data: ItemUpdate,
    current_user = Depends(check_resource_owner(resource_type="item"))
):
    # 현재 사용자가 아이템 소유자임이 이미 확인되었으므로 바로 업데이트 가능
    return update_item_service(item_id, item_data)
```

### 권한 체크

특정 권한이 있는지 확인합니다.

```python
from app.common.dependencies.permissions import has_permission

@app.delete("/items/{item_id}")
async def delete_item(
    item_id: int,
    _ = Depends(has_permission("delete_item"))
):
    return delete_item_service(item_id)
```

## 페이지네이션 의존성

[@pagination](/fastapi_template/app/common/dependencies/pagination.py)

### 페이지네이션 파라미터

```python
from app.common.dependencies.pagination import pagination_params

@app.get("/items-list")
async def list_items(
    pagination = Depends(pagination_params),
    db = Depends(get_db)
):
    skip, limit = pagination["skip"], pagination["limit"]
    return db.query(Item).offset(skip).limit(limit).all()
```

## 사용 예시

여러 의존성을 조합하여 사용할 수 있습니다:

```python
@app.get("/user/items")
async def get_user_items(
    pagination = Depends(pagination_params),
    current_user = Depends(get_current_active_user),
    db = Depends(get_db)
):
    skip, limit = pagination["skip"], pagination["limit"]
    return db.query(Item).filter(Item.owner_id == current_user.id)\
             .offset(skip).limit(limit).all()
```

## 사용자 정의 의존성 작성

새로운 의존성 함수를 작성할 때는 다음과 같은 패턴을 따르면 좋습니다:

```python
# app/common/dependencies/custom.py
from fastapi import Depends, HTTPException, status
from app.common.dependencies.auth import get_current_user

def custom_dependency(param1: str, param2: int = 10):
    def _custom_dependency(current_user = Depends(get_current_user)):
        # 의존성 로직 구현
        if not validate_something(param1, param2, current_user):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="요청을 처리할 수 없습니다."
            )
        return {"param1": param1, "param2": param2, "user_id": current_user.id}
    return _custom_dependency
```

사용:

```python
@app.get("/custom-endpoint")
async def custom_endpoint(
    custom_data = Depends(custom_dependency("value1", 20))
):
    return custom_data
```
