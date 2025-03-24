"""
# File: fastapi_template/app/common/__init__.py
# Description: 공통 모듈 패키지 초기화
# - 모든 공통 모듈을 임포트하고 내보냄
"""

# 순환 참조 방지를 위해 명시적 import 사용

# 공통 모듈 - 상대 경로 사용
# from . import auth  # 테스트를 위해 임시 주석 처리
# from . import cache  # 테스트를 위해 임시 주석 처리
from . import config
# from . import database  # 테스트를 위해 임시 주석 처리
# from . import dependencies  # 테스트를 위해 임시 주석 처리
# from . import exceptions  # 테스트를 위해 임시 주석 처리
# from . import middleware  # 테스트를 위해 임시 주석 처리
# from . import monitoring  # 테스트를 위해 임시 주석 처리
# from . import schemas  # 테스트를 위해 임시 주석 처리
# from . import security  # 테스트를 위해 임시 주석 처리
# from . import utils  # 테스트를 위해 임시 주석 처리
# from . import validators  # 테스트를 위해 임시 주석 처리

# 버전 정보
__version__ = "0.1.0"

# 모듈 export
__all__ = [
    # "auth",  # 테스트를 위해 임시 주석 처리
    # "cache",  # 테스트를 위해 임시 주석 처리
    "config",
    # "database",  # 테스트를 위해 임시 주석 처리
    # "dependencies",  # 테스트를 위해 임시 주석 처리
    # "exceptions",  # 테스트를 위해 임시 주석 처리
    # "middleware",  # 테스트를 위해 임시 주석 처리
    # "monitoring",  # 테스트를 위해 임시 주석 처리
    # "schemas",  # 테스트를 위해 임시 주석 처리
    # "security",  # 테스트를 위해 임시 주석 처리
    # "utils",  # 테스트를 위해 임시 주석 처리
    # "validators",  # 테스트를 위해 임시 주석 처리
    "__version__",
]
