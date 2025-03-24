"""
Python-dotenv 테스트 스크립트
"""

import tempfile
import os
from dotenv import dotenv_values, load_dotenv

def test_dotenv():
    """python-dotenv 테스트"""
    
    # 테스트용 .env 파일 내용 생성 - 들여쓰기 없이
    content = """# 테스트 설정
APP_NAME=TestApp
DEBUG=true
API_PREFIX=/api/v3
"""
    
    # 임시 파일에 쓰기 (인코딩 지정)
    with tempfile.NamedTemporaryFile(mode='w', encoding='utf-8', delete=False) as temp:
        temp.write(content)
        temp_name = temp.name
        print(f'파일 경로: {temp_name}')
    
    try:
        # 파일 내용 출력
        with open(temp_name, 'r', encoding='utf-8') as f:
            print('\n파일 내용:')
            print(f.read())
        
        # python-dotenv로 로드
        config = dotenv_values(dotenv_path=temp_name, encoding='utf-8')
        print('\nPython-dotenv 로드 결과:')
        print(config)
        
        # 값 확인
        print('\n설정 값:')
        print(f"APP_NAME: {config.get('APP_NAME')}")
        print(f"DEBUG: {config.get('DEBUG')}")
        print(f"API_PREFIX: {config.get('API_PREFIX')}")
        
        # 또는 load_dotenv를 사용하여 os.environ에 로드
        load_dotenv(dotenv_path=temp_name, encoding='utf-8')
        print('\nos.environ 로드 결과:')
        print(f"APP_NAME: {os.environ.get('APP_NAME')}")
        print(f"DEBUG: {os.environ.get('DEBUG')}")
        print(f"API_PREFIX: {os.environ.get('API_PREFIX')}")
        
    finally:
        # 임시 파일 삭제
        os.unlink(temp_name)

if __name__ == "__main__":
    test_dotenv() 