# 인증 모듈 상세 가이드

이 문서는 FastAPI 템플릿의 인증 모듈에 대한 상세 사용법과 설명을 제공합니다.

## 목차

- [JWT 인증](#jwt-인증)
- [비밀번호 해싱](#비밀번호-해싱)
- [인증 미들웨어](#인증-미들웨어)
- [권한 처리](#권한-처리)

## JWT 인증

JWT(JSON Web Token)는 클라이언트-서버 간 인증 정보를 안전하게 전달하는 표준 방식입니다.

### 토큰 생성

```python
from app.common.auth import create_access_token

# 기본 설정으로 토큰 생성
token = create_access_token(subject=user_id)

# 만료 시간 지정
token = create_access_token(subject=user_id, expires_delta=timedelta(hours=1))

# 추가 데이터 포함
token = create_access_token(
    subject=user_id,
    data={"role": "admin", "permissions": ["read", "write"]}
)
```

### 토큰 검증

```python
from app.common.auth import verify_token

# 토큰 검증
try:
    payload = verify_token(token)
    user_id = payload.get("sub")
except JWTError:
    raise AuthenticationError("유효하지 않은 인증 토큰입니다")
```

### 리프레시 토큰

```python
from app.common.auth import create_refresh_token, refresh_access_token

# 리프레시 토큰 생성
refresh_token = create_refresh_token(subject=user_id)

# 리프레시 토큰으로 새 액세스 토큰 발급
new_access_token = refresh_access_token(refresh_token)
```

## 비밀번호 해싱

사용자 비밀번호는 안전한 해싱 알고리즘(기본값: bcrypt)을 사용하여 저장됩니다.

### 비밀번호 해싱

```python
from app.common.auth import get_password_hash

# 비밀번호 해싱
hashed_password = get_password_hash("raw_password")
```

### 비밀번호 검증

```python
from app.common.auth import verify_password

# 비밀번호 검증
is_valid = verify_password("raw_password", hashed_password)
```

## 인증 미들웨어

### JWTBearer

FastAPI 엔드포인트에 인증을 적용하기 위한 의존성입니다.

```python
from fastapi import Depends
from app.common.auth import JWTBearer

# 엔드포인트에 인증 적용
@app.get("/protected", dependencies=[Depends(JWTBearer())])
async def protected_route():
    return {"message": "인증된 사용자만 접근 가능합니다"}

# 현재 인증된 사용자 정보 가져오기
@app.get("/me")
async def get_me(current_user = Depends(JWTBearer())):
    return current_user
```

### 선택적 인증

일부 엔드포인트에서는 인증이 선택적일 수 있습니다.

```python
from app.common.auth import OptionalJWTBearer

@app.get("/items")
async def get_items(current_user = Depends(OptionalJWTBearer())):
    if current_user:
        return {"message": "인증된 사용자 접근", "user_id": current_user.id}
    return {"message": "익명 사용자 접근"}
```

## 권한 처리

### 역할 기반 접근 제어

```python
from app.common.auth import RoleChecker

# 특정 역할만 접근 가능
admin_only = RoleChecker(["admin"])
editor_or_admin = RoleChecker(["editor", "admin"])

@app.get("/admin", dependencies=[Depends(admin_only)])
async def admin_route():
    return {"message": "관리자만 접근 가능합니다"}

@app.get("/content", dependencies=[Depends(editor_or_admin)])
async def content_route():
    return {"message": "편집자 또는 관리자만 접근 가능합니다"}
```

### 권한 기반 접근 제어

```python
from app.common.auth import PermissionChecker

# 특정 권한만 접근 가능
can_delete = PermissionChecker(["delete"])
can_create_users = PermissionChecker(["create_user"])

@app.delete("/items/{item_id}", dependencies=[Depends(can_delete)])
async def delete_item(item_id: int):
    return {"message": f"아이템 {item_id} 삭제됨"}

@app.post("/users", dependencies=[Depends(can_create_users)])
async def create_user(user_data: dict):
    return {"message": "사용자 생성됨"}
```

## 인증 설정

`app/common/config/auth_settings.py`에서 인증 관련 설정을 변경할 수 있습니다.

```python
# 설정 예시
SECRET_KEY = "your-secret-key"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30
REFRESH_TOKEN_EXPIRE_DAYS = 7
``` 