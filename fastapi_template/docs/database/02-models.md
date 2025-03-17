# 모델 정의

이 문서는 FastAPI 프로젝트에서 SQLAlchemy를 사용한 데이터베이스 모델 정의 방법을 설명합니다.

## 목차

1. [모델 구조](#모델-구조)
2. [사용자 모델](#사용자-모델)
3. [아이템 모델](#아이템-모델)
4. [관계 정의](#관계-정의)

## 모델 구조

모델은 `app/db/models/` 디렉토리에 정의됩니다. 각 모델은 `app/common/database/base.py`에 정의된 `BaseModel` 클래스를 상속받습니다.

```
app/
└── db/
    └── models/
        ├── __init__.py
        ├── user.py
        └── item.py
```

## 사용자 모델

`app/db/models/user.py`에 사용자 모델을 정의합니다:

```python
from sqlalchemy import Boolean, Column, String
from sqlalchemy.orm import relationship

from app.common.database.base import BaseModel


class User(BaseModel):
    """
    사용자 모델
    """
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    full_name = Column(String, nullable=True)
    is_active = Column(Boolean, default=True)
    is_superuser = Column(Boolean, default=False)
    
    # 관계 정의
    items = relationship("Item", back_populates="owner")
    
    def __repr__(self):
        return f"<User {self.email}>"
```

### 주요 필드

- **email**: 사용자 이메일 (고유 식별자)
- **hashed_password**: 암호화된 비밀번호
- **full_name**: 사용자 전체 이름 (선택 사항)
- **is_active**: 계정 활성화 상태
- **is_superuser**: 관리자 권한 여부

## 아이템 모델

`app/db/models/item.py`에 아이템 모델을 정의합니다:

```python
from sqlalchemy import Column, ForeignKey, String, Text
from sqlalchemy.orm import relationship

from app.common.database.base import BaseModel


class Item(BaseModel):
    """
    아이템 모델
    """
    title = Column(String(100), index=True, nullable=False)
    description = Column(Text, nullable=True)
    owner_id = Column(Integer, ForeignKey("user.id"), nullable=False)
    
    # 관계 정의
    owner = relationship("User", back_populates="items")
    
    def __repr__(self):
        return f"<Item {self.title}>"
```

### 주요 필드

- **title**: 아이템 제목
- **description**: 아이템 설명 (선택 사항)
- **owner_id**: 소유자 ID (외래 키)

## 관계 정의

SQLAlchemy에서는 `relationship` 함수를 사용하여 모델 간의 관계를 정의합니다:

### 일대다 관계 (One-to-Many)

사용자와 아이템 간의 일대다 관계:

```python
# User 모델에서
items = relationship("Item", back_populates="owner")

# Item 모델에서
owner = relationship("User", back_populates="items")
```

### 다대다 관계 (Many-to-Many)

다대다 관계는 연결 테이블을 사용하여 정의합니다:

```python
# 연결 테이블 정의
user_group = Table(
    "user_group",
    Base.metadata,
    Column("user_id", Integer, ForeignKey("user.id"), primary_key=True),
    Column("group_id", Integer, ForeignKey("group.id"), primary_key=True)
)

# User 모델에서
groups = relationship("Group", secondary=user_group, back_populates="users")

# Group 모델에서
users = relationship("User", secondary=user_group, back_populates="groups")
```

## 모델 가져오기

`app/db/models/__init__.py`에서 모든 모델을 가져와 Alembic 마이그레이션에서 사용할 수 있도록 합니다:

```python
from app.db.models.user import User
from app.db.models.item import Item

# 추가 모델을 여기에 가져옵니다
```

## 다음 단계

다음 문서에서는 [마이그레이션 설정](./03-migrations.md)에 대해 알아보겠습니다.
