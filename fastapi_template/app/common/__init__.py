"""
# File: fastapi_template/app/common/__init__.py
# Description: 공통 모듈 패키지 초기화
# - 모든 공통 모듈을 임포트하고 내보냄
"""

# 순환 참조 방지를 위해 명시적 import 사용

# 공통 모듈
from app.common import auth
from app.common import cache
from app.common import config
from app.common import database
from app.common import dependencies
from app.common import exceptions
from app.common import middleware
from app.common import monitoring
from app.common import schemas
from app.common import security
from app.common import utils
from app.common import validators

# 버전 정보
__version__ = "0.1.0"

# 모듈 export
__all__ = [
    "auth",
    "cache",
    "config",
    "database",
    "dependencies",
    "exceptions",
    "middleware",
    "monitoring",
    "schemas",
    "security",
    "utils",
    "validators",
    "__version__",
]
