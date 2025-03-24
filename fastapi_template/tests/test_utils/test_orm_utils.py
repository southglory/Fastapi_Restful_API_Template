"""
SQLAlchemy ORM 유틸리티 테스트
"""
import pytest
from unittest.mock import Mock, patch
from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import declarative_base

from app.common.utils.orm_utils import get_python_value

# SQLAlchemy 기본 베이스 클래스 생성
Base = declarative_base()


# 테스트를 위한 샘플 모델 정의
class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True)
    name = Column(String(50))
    email = Column(String(100))


class TestOrmUtils:
    """ORM 유틸리티 테스트 클래스"""
    
    def test_get_python_value_with_regular_value(self):
        """일반 Python 값에서 변환 테스트"""
        # 정수 값 테스트
        assert get_python_value(10) == 10
        
        # 문자열 값 테스트
        assert get_python_value("test") == "test"
        
        # None 값 테스트 (기본값 지정)
        assert get_python_value(None, default_value="기본값") == "기본값"
        
        # None 값 테스트 (기본값 없음)
        assert get_python_value(None) is None
    
    def test_get_python_value_with_sqlalchemy_column(self):
        """SQLAlchemy Column에서 값 추출 테스트"""
        # Column 모킹
        mock_column = Mock(spec=Column)
        mock_column._annotations = {"value": 42}
        
        # Column에서 값 추출
        result = get_python_value(mock_column)
        assert result == 42
    
    def test_get_python_value_with_column_no_annotation(self):
        """_annotations에 value가 없는 Column 테스트"""
        # 비어있는 _annotations를 가진 Column 모킹
        mock_column = Mock(spec=Column)
        mock_column._annotations = {}
        
        # 기본값 설정
        result = get_python_value(mock_column, default_value=100)
        assert result == 100
    
    @patch('sqlalchemy.orm.attributes.InstrumentedAttribute')
    def test_get_python_value_with_sample_model(self, mock_attr):
        """샘플 모델 칼럼 테스트 (모의 객체 사용)"""
        # 모의 InstrumentedAttribute 생성
        mock_column = Mock()
        mock_column._annotations = {"value": 1}
        
        # get_python_value 함수에서 사용될 때 모의 객체 반환
        with patch('app.common.utils.orm_utils.isinstance', return_value=True):
            result = get_python_value(mock_column)
            assert result == 1 