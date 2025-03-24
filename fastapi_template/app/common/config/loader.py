"""
# File: app/common/config/loader.py
# Description: 환경변수와 설정 파일에서 설정을 로드하는 모듈
"""

import os
import json
from typing import Dict, Any, Optional, Union, List
from dotenv import load_dotenv, dotenv_values
# 참고: load_dotenv는 환경 변수를 os.environ에 직접 로드하는 반면,
# dotenv_values는 환경 변수를 딕셔너리로 반환합니다.
# 이 모듈에서는 설정을 격리된 딕셔너리로 관리하기 위해 주로 dotenv_values를 사용합니다.
# 이는 설정의 유연성과 테스트 가능성을 높이기 위한 선택입니다.


def load_env_vars(var_names: Optional[List[str]] = None, prefix: str = "") -> Dict[str, str]:
    """
    환경 변수에서 설정을 로드합니다.
    
    Args:
        var_names: 로드할 환경 변수 이름 목록 (None이면 모든 변수)
        prefix: 환경 변수 접두사 (예: "APP_")
        
    Returns:
        환경 변수에서 로드된 설정
    """
    env_vars = {}
    prefix_len = len(prefix)
    
    # 특정 변수 이름 목록이 제공된 경우
    if var_names is not None:
        for name in var_names:
            if name in os.environ:
                env_vars[name] = os.environ[name]
        return env_vars
    
    # 접두사로 필터링하는 경우
    for key, value in os.environ.items():
        if prefix and not key.startswith(prefix):
            continue
            
        env_key = key[prefix_len:] if prefix else key
        env_vars[env_key] = value
        
    return env_vars


def load_env_file(file_path: str) -> Dict[str, str]:
    """
    .env 파일에서 설정을 로드합니다.
    
    Args:
        file_path: .env 파일 경로
        
    Returns:
        .env 파일에서 로드된 설정
        
    참고:
        dotenv_values는 환경 변수를 os.environ에 로드하지 않고 딕셔너리로 반환합니다.
        이는 여러 설정 소스를 병합하고 테스트에서 격리된 환경을 유지하기 위함입니다.
        프로세스 전체에 영향을 주는 load_dotenv와 달리 더 유연한 설정 관리가 가능합니다.
    """
    if not os.path.exists(file_path):
        return {}
    
    try:
        # python-dotenv의 dotenv_values 함수 사용 (인코딩 명시)
        return dotenv_values(file_path, encoding="utf-8")
    except Exception:
        # 파일 로드 오류는 무시하고 빈 설정 반환
        return {}


def load_json_config(file_path: str) -> Dict[str, Any]:
    """
    JSON 파일에서 설정을 로드합니다.
    
    Args:
        file_path: JSON 파일 경로
        
    Returns:
        JSON 파일에서 로드된 설정
    """
    if not os.path.exists(file_path):
        return {}
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception:
        # 파일 로드 오류는 무시하고 빈 설정 반환
        return {}


def get_env_setting(
    key: str, 
    default: Any = None, 
    prefix: str = "", 
    required: bool = False
) -> Any:
    """
    환경 변수에서 특정 설정을 가져옵니다.
    
    Args:
        key: 가져올 설정 키
        default: 설정이 없을 경우 기본값
        prefix: 환경 변수 접두사
        required: 필수 여부 (필수인데 없으면 예외 발생)
        
    Returns:
        환경 변수 값 또는 기본값
        
    Raises:
        ValueError: 필수 설정이 없을 경우
    """
    env_key = f"{prefix}{key}"
    value = os.environ.get(env_key)
    
    if value is None:
        if required:
            raise ValueError(f"필수 환경 변수가 없습니다: {env_key}")
        return default
    
    return value


def merge_configs(*configs: Dict[str, Any]) -> Dict[str, Any]:
    """
    여러 설정을 병합합니다. 뒤에 오는 설정이 앞의 설정을 덮어씁니다.
    중첩된 딕셔너리의 경우 깊은 병합을 수행합니다.
    
    Args:
        *configs: 병합할 설정 딕셔너리들
        
    Returns:
        병합된 설정
    """
    def deep_merge(base: Dict[str, Any], override: Dict[str, Any]) -> Dict[str, Any]:
        """중첩된 딕셔너리를 깊은 병합"""
        result = base.copy()
        for key, value in override.items():
            if key in result and isinstance(result[key], dict) and isinstance(value, dict):
                result[key] = deep_merge(result[key], value)
            else:
                result[key] = value
        return result
    
    if not configs:
        return {}
    
    result = configs[0].copy()
    for config in configs[1:]:
        result = deep_merge(result, config)
    
    return result 