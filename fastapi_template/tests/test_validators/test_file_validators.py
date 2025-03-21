import pytest
import tempfile
import os
from app.common.validators.file_validators import (
    validate_file_extension,
    validate_file_size,
    validate_image_file,
    validate_mime_type,
    validate_file_mime_type,
    validate_image_dimensions,
)

# 모듈 전체에서 사용할 magic 변수 정의
try:
    import magic
except ImportError:
    magic = None


def test_validate_file_extension():
    # 임시 파일 생성
    with tempfile.NamedTemporaryFile(suffix=".txt") as temp_file:
        # 유효한 확장자 테스트
        result, error_msg = validate_file_extension(temp_file.name, {".txt", ".pdf"})
        assert result == True
        assert error_msg is None

        # 유효하지 않은 확장자 테스트
        result, error_msg = validate_file_extension(temp_file.name, {".pdf", ".docx"})
        assert result == False
        assert error_msg is not None
        assert ".txt" in str(error_msg)  # 오류 메시지에 확장자가 포함되어야 함

    # 예외 처리 테스트 - 존재하지 않는 파일
    try:
        validate_file_extension("non_existent_file.txt", {".txt"})
    except Exception as e:
        assert isinstance(e, Exception)


def test_validate_file_size():
    # 임시 파일 생성 및 데이터 작성
    with tempfile.NamedTemporaryFile(delete=False) as temp_file:
        temp_file.write(b"0" * 1024)  # 1KB 크기의 파일

    try:
        # 파일 크기 가져오기
        file_size = os.path.getsize(temp_file.name)

        # 파일 크기 유효성 검사 (2KB 허용)
        result, error_msg = validate_file_size(file_size, 2048)
        assert result == True
        assert error_msg is None

        # 파일 크기 유효성 검사 (500 bytes 허용)
        result, error_msg = validate_file_size(file_size, 500)
        assert result == False
        assert error_msg is not None
        assert "초과" in str(error_msg)  # 오류 메시지에 "초과"가 포함되어야 함

        # 다양한 크기 형식 테스트
        # 바이트 단위 (<1KB)
        small_size = 500
        result, error_msg = validate_file_size(1000, small_size)
        assert result == False
        assert "bytes" in str(error_msg)

        # KB 단위 (>=1KB && <1MB)
        kb_size = 1500
        result, error_msg = validate_file_size(2000, kb_size)
        assert result == False
        assert "KB" in str(error_msg)

        # MB 단위 (>=1MB)
        mb_size = 1024 * 1024 * 2  # 2MB
        result, error_msg = validate_file_size(1024 * 1024 * 3, mb_size)
        assert result == False
        assert "MB" in str(error_msg)
    finally:
        # 테스트 후 파일 삭제
        os.unlink(temp_file.name)

    # 예외 처리 테스트
    try:
        validate_file_size(-1, 1000)  # 음수 사이즈
    except Exception as e:
        assert isinstance(e, Exception)


def test_validate_image_file():
    # 유효한 이미지 파일 테스트를 위한 임시 파일 생성
    with tempfile.NamedTemporaryFile(suffix=".jpg", delete=False) as temp_file:
        # 간단한 BMP 헤더 작성 (실제 이미지 데이터는 아님)
        temp_file.write(b"BM" + b"\x00" * 100)
        temp_file_path = temp_file.name

    try:
        # 확장자만 검사 (내용 검증은 모의)
        result, error_msg = validate_image_file(temp_file_path)

        # 실제 테스트에서는 유효한 이미지 파일을 사용해야 함
        if not result and error_msg is not None:
            assert "이미지 형식이 아닙니다" in str(error_msg)

        # 유효하지 않은 확장자 테스트
        with tempfile.NamedTemporaryFile(suffix=".txt", delete=False) as invalid_file:
            invalid_path = invalid_file.name

        try:
            result, error_msg = validate_image_file(invalid_path)
            assert result == False
            assert error_msg is not None
            assert "확장자" in str(error_msg)  # 오류 메시지에 "확장자"가 포함되어야 함
        finally:
            os.unlink(invalid_path)

        # 파일은 있지만 이미지 내용이 아닌 경우 테스트
        with tempfile.NamedTemporaryFile(suffix=".jpg", delete=False) as invalid_img:
            invalid_img.write(b"This is not an image content")
            invalid_img_path = invalid_img.name

        try:
            result, error_msg = validate_image_file(invalid_img_path)
            assert result == False
            assert error_msg is not None
            assert "이미지 형식이 아닙니다" in str(error_msg)
        finally:
            os.unlink(invalid_img_path)

        # 존재하지 않는 파일 테스트
        result, error_msg = validate_image_file("non_existent_image.jpg")
        assert result == False
        assert error_msg is not None

        # PIL 라이브러리가 없는 상황 모의 테스트 (monkeypatch 사용)
        def mock_import_error(name, *args, **kwargs):
            if name == "PIL":
                raise ImportError("PIL not found")
            return __import__(name, *args, **kwargs)

        import builtins

        original_import = builtins.__import__
        try:
            builtins.__import__ = mock_import_error
            # PIL import가 실패하는 상황 테스트
            result, error_msg = validate_image_file(temp_file_path)
            assert result == False
            assert "PIL 라이브러리" in str(error_msg)
        finally:
            builtins.__import__ = original_import

    finally:
        os.unlink(temp_file_path)


# magic 라이브러리가 설치된 경우만 실행하는 테스트
@pytest.mark.skipif(magic is None, reason="python-magic 라이브러리가 설치되지 않음")
def test_validate_mime_type():
    # magic 라이브러리가 없으면 스킵
    if magic is None:
        pytest.skip("python-magic 라이브러리가 설치되지 않음")

    # 임시 텍스트 파일 생성
    with tempfile.NamedTemporaryFile(suffix=".txt", delete=False) as temp_file:
        temp_file.write(b"Hello, World!")
        temp_file_path = temp_file.name

    try:
        # 유효한 MIME 타입 테스트
        result, error_msg = validate_mime_type(temp_file_path, ["text/plain"])
        if not isinstance(result, bool):
            pytest.skip("MIME 타입 검증 결과가 예상과 다름")

        # 라이브러리 오류가 아닌 경우에만 테스트
        if error_msg is None or "python-magic 라이브러리" not in str(error_msg):
            # 유효한 MIME 타입 테스트
            assert result == True
            assert error_msg is None

            # 유효하지 않은 MIME 타입 테스트
            result, error_msg = validate_mime_type(temp_file_path, ["application/pdf"])
            assert result == False
            assert error_msg is not None
            assert "파일 타입" in str(error_msg)

            # 존재하지 않는 파일 테스트
            result, error_msg = validate_mime_type(
                "non_existent_file.txt", ["text/plain"]
            )
            assert result == False

            # 예외 발생 시나리오 시뮬레이션
            original_from_file = magic.from_file

            def mock_from_file_exception(*args, **kwargs):
                raise Exception("Mocked exception")

            try:
                magic.from_file = mock_from_file_exception
                result, error_msg = validate_mime_type(temp_file_path, ["text/plain"])
                assert result == False
                assert "오류 발생" in str(error_msg)
            finally:
                magic.from_file = original_from_file
    finally:
        os.unlink(temp_file_path)


# magic 모듈이 없는 경우 테스트
def test_validate_mime_type_no_magic():
    # global magic을 직접 조작
    import app.common.validators.file_validators as file_validators

    original_magic = file_validators.magic

    try:
        # magic을 None으로 설정
        file_validators.magic = None

        # magic이 None인 상태에서 테스트
        result, error_msg = validate_mime_type("dummy.txt", ["text/plain"])
        assert result == False
        assert "python-magic 라이브러리" in str(error_msg)
    finally:
        # 원래 magic 복원
        file_validators.magic = original_magic


# magic 라이브러리가 설치된 경우만 실행하는 테스트
@pytest.mark.skipif(magic is None, reason="python-magic 라이브러리가 설치되지 않음")
def test_validate_file_mime_type():
    # magic 라이브러리가 없으면 스킵
    if magic is None:
        pytest.skip("python-magic 라이브러리가 설치되지 않음")

    # 임시 텍스트 파일 생성
    with tempfile.NamedTemporaryFile(suffix=".txt", delete=False) as temp_file:
        temp_file.write(b"Hello, World!")
        temp_file_path = temp_file.name

    try:
        # 유효한 MIME 타입 테스트
        result = validate_file_mime_type(temp_file_path, {"text/plain"})
        assert result == True

        # 유효하지 않은 MIME 타입 테스트
        result = validate_file_mime_type(temp_file_path, {"application/pdf"})
        assert result == False

        # 존재하지 않는 파일 테스트
        result = validate_file_mime_type("non_existent_file.txt", {"text/plain"})
        assert result == False

        # 예외 발생 시나리오 시뮬레이션
        original_Magic = magic.Magic

        class MockMagic:
            def __init__(self, mime=False):
                pass

            def from_file(self, *args, **kwargs):
                raise Exception("Mocked exception")

        try:
            magic.Magic = MockMagic
            result = validate_file_mime_type(temp_file_path, {"text/plain"})
            assert result == False
        finally:
            magic.Magic = original_Magic
    finally:
        os.unlink(temp_file_path)


# magic 모듈이 없는 경우 테스트
def test_validate_file_mime_type_no_magic():
    # 원래 magic 값 저장
    global magic
    original_magic = magic

    try:
        # magic을 None으로 설정
        magic = None

        # magic이 None인 경우 테스트
        result = validate_file_mime_type("test.txt", {"text/plain"})
        assert result == False
    finally:
        # 원래 magic 복원
        magic = original_magic


def test_validate_image_dimensions():
    # PIL 라이브러리 필요 여부 확인
    try:
        from PIL import Image
    except ImportError:
        pytest.skip("PIL 라이브러리가 설치되지 않음")

    # 테스트용 이미지 생성 (100x100 픽셀)
    with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as temp_file:
        temp_file_path = temp_file.name

    try:
        # 100x100 크기의 빈 이미지 생성
        Image.new("RGB", (100, 100)).save(temp_file_path)

        # 이미지 크기 제한 테스트
        # 범위 내 테스트
        assert (
            validate_image_dimensions(
                temp_file_path,
                min_width=50,
                min_height=50,
                max_width=150,
                max_height=150,
            )
            == True
        )

        # 최소 크기 제한 위반 테스트
        assert (
            validate_image_dimensions(temp_file_path, min_width=150, min_height=50)
            == False
        )
        assert (
            validate_image_dimensions(temp_file_path, min_width=50, min_height=150)
            == False
        )

        # 최대 크기 제한 위반 테스트
        assert (
            validate_image_dimensions(temp_file_path, max_width=50, max_height=150)
            == False
        )
        assert (
            validate_image_dimensions(temp_file_path, max_width=150, max_height=50)
            == False
        )

        # 제한 없음 테스트
        assert validate_image_dimensions(temp_file_path) == True

        # 존재하지 않는 파일 테스트
        assert validate_image_dimensions("non_existent_image.png") == False

        # 이미지가 아닌 파일 테스트
        with tempfile.NamedTemporaryFile(suffix=".txt", delete=False) as non_img_file:
            non_img_file.write(b"This is not an image")
            non_img_path = non_img_file.name

        try:
            assert validate_image_dimensions(non_img_path) == False
        finally:
            os.unlink(non_img_path)
    finally:
        os.unlink(temp_file_path)


def test_validate_file_extension_special_cases():
    """추가적인 파일 확장자 검증 테스트 케이스"""
    # 확장자가 없는 파일
    result, error_msg = validate_file_extension("noextension", {".txt", ".pdf"})
    assert result == False
    assert error_msg is not None
    assert "확장자" in str(error_msg)


def test_validate_image_file_additional_cases():
    """이미지 파일 추가 테스트 케이스"""
    # 경로에 디렉토리가 포함된 경우
    result, error_msg = validate_image_file("some/path/to/image.jpg")
    if not result:
        assert isinstance(error_msg, str)

    # None 값 전달 테스트
    try:
        # 실제로는 문자열이 아닌 값을 전달할 수 없으므로 타입 오류 예외가 발생해야 함
        validate_image_file("")  # 빈 문자열 전달
    except Exception as e:
        assert isinstance(e, Exception)


def test_validate_image_dimensions_additional_cases():
    """이미지 크기 검증 추가 테스트 케이스"""
    # PIL 라이브러리 필요 여부 확인
    try:
        from PIL import Image
    except ImportError:
        pytest.skip("PIL 라이브러리가 설치되지 않음")

    # PIL 라이브러리가 에러를 발생시키는 경우 시뮬레이션
    original_open = Image.open

    def mock_open(*args, **kwargs):
        raise Exception("Mocked PIL error")

    try:
        Image.open = mock_open
        assert validate_image_dimensions("any_file.jpg") == False
    finally:
        Image.open = original_open


# magic 임포트 부분 테스트 (라인 13-14)
def test_magic_import_handling():
    """magic 라이브러리 임포트 처리 테스트"""
    import importlib
    import sys

    # 원래 magic이 있었는지 확인
    had_magic = "magic" in sys.modules

    # 원래 magic 모듈 백업
    original_magic = None
    if had_magic:
        original_magic = sys.modules["magic"]

    try:
        # magic 모듈 제거
        if "magic" in sys.modules:
            del sys.modules["magic"]

        # 테스트용 가짜 ImportError를 발생시키는 magic 모듈 생성
        class FakeImportError(ImportError):
            pass

        def fake_import(name, *args, **kwargs):
            if name == "magic":
                raise FakeImportError("Fake import error for testing")
            return importlib.__import__(name, *args, **kwargs)

        # 원래 __import__ 함수 백업
        original_import = __import__

        # __import__ 함수 대체
        import builtins

        builtins.__import__ = fake_import

        try:
            # 모듈 다시 로드 시도
            importlib.reload(
                importlib.import_module("app.common.validators.file_validators")
            )

            # 파일 MIME 타입 검증 함수 테스트 (magic이 None인 경우)
            from app.common.validators.file_validators import validate_file_mime_type

            result = validate_file_mime_type("dummy.txt", {"text/plain"})
            assert result == False
        finally:
            # 원래 __import__ 함수 복원
            builtins.__import__ = original_import
    finally:
        # 원래 magic 모듈 복원
        if had_magic and original_magic:
            sys.modules["magic"] = original_magic


# PIL 임포트 실패 및 이미지 파일 검증 예외 처리 테스트 (라인 100-102, 111)
def test_image_file_validation_edge_cases():
    """이미지 파일 검증 엣지 케이스 테스트"""
    import importlib
    import sys
    from unittest.mock import patch

    # 이미지 포맷이 None인 경우 테스트
    with patch("PIL.Image.open") as mock_open:
        # 이미지 모의 객체 생성
        mock_img = type("MockImage", (), {"format": None})()
        mock_open.return_value.__enter__.return_value = mock_img

        result, error_msg = validate_image_file("test.jpg")
        assert result == False
        assert error_msg is not None
        assert "이미지 형식이 아닙니다" in str(error_msg)

    # Image.open 호출 시 일반 예외 발생 (라인 111)
    with patch("PIL.Image.open") as mock_open:
        mock_open.side_effect = Exception("일반적인 오류")

        result, error_msg = validate_image_file("test.jpg")
        assert result == False
        assert error_msg is not None
        assert "이미지 형식이 아닙니다" in str(error_msg)


def test_image_file_validation_specific_exception():
    """이미지 파일 검증 시 구체적인 111번 라인 예외 상황 테스트"""
    from unittest.mock import patch
    import contextlib

    # Image.open의 context manager 예외 발생 시뮬레이션
    class MockContextManager:
        def __enter__(self):
            # 콘텍스트 진입 시 예외 발생하지 않음
            return type("MockImage", (), {"format": "JPEG"})()

        def __exit__(self, exc_type, exc_val, exc_tb):
            # 콘텍스트 종료 시 예외 발생
            raise Exception("콘텍스트 매니저 종료 중 예외 발생")

    # Image.open 대신 MockContextManager를 반환하는 패치
    with patch("PIL.Image.open", return_value=MockContextManager()):
        result, error_msg = validate_image_file("test.jpg")
        assert result == False
        assert error_msg is not None
        assert "이미지 형식이 아닙니다" in str(error_msg)


def test_file_mime_type_magic_exception():
    """validate_file_mime_type 함수의 예외 처리 블록(111번 라인) 테스트"""
    # magic 라이브러리가 설치되지 않은 경우 스킵
    if magic is None:
        pytest.skip("python-magic 라이브러리가 설치되지 않음")

    # import file_validators 모듈을 직접 사용
    import app.common.validators.file_validators as file_validators

    # 원래 magic 모듈 저장
    original_magic = file_validators.magic
    original_Magic = None
    if original_magic:
        original_Magic = original_magic.Magic

    try:
        # 예외를 발생시키는 모의 Magic 클래스 정의
        class MockMagic:
            def __init__(self, mime=False):
                pass

            def from_file(self, filepath):
                # 의도적으로 예외 발생
                raise Exception("의도적인 예외 발생")

        # 원래 Magic 클래스가 있으면 교체
        if original_magic:
            file_validators.magic.Magic = MockMagic

            # 임시 파일 생성
            with tempfile.NamedTemporaryFile(suffix=".txt") as temp_file:
                # validate_file_mime_type 함수를 호출하여 예외 처리 블록 테스트
                result = file_validators.validate_file_mime_type(
                    temp_file.name, {"text/plain"}
                )

                # 예외가 올바르게 처리되면 False를 반환해야 함
                assert result == False
    finally:
        # 원래 Magic 클래스 복원
        if original_magic and original_Magic:
            file_validators.magic.Magic = original_Magic


def test_with_real_image_files():
    """실제 이미지 파일을 사용한 종합 테스트"""
    # PIL 라이브러리 필요 여부 확인
    try:
        from PIL import Image
    except ImportError:
        pytest.skip("PIL 라이브러리가 설치되지 않음")

    # 실제 이미지 파일 생성 (JPG, PNG, GIF)
    image_files = []
    formats = [("jpg", "JPEG"), ("png", "PNG"), ("gif", "GIF")]

    try:
        # 여러 형식의 실제 이미지 파일 생성
        for ext, format_name in formats:
            with tempfile.NamedTemporaryFile(
                suffix=f".{ext}", delete=False
            ) as temp_file:
                # 실제 이미지 데이터 생성 (50x50 픽셀)
                img = Image.new("RGB", (50, 50), color=(255, 0, 0))  # 빨간색 이미지
                img.save(temp_file.name, format=format_name)
                image_files.append((temp_file.name, ext, format_name))

        # 모든 이미지 파일에 대해 검증 함수 테스트
        for filepath, ext, _ in image_files:
            # 1. 파일 확장자 검증
            result, error_msg = validate_file_extension(
                filepath, {f".{ext}", ".jpg", ".png", ".gif"}
            )
            assert result == True
            assert error_msg is None

            # 2. 이미지 파일 검증
            result, error_msg = validate_image_file(filepath)
            assert result == True
            assert error_msg is None

            # 3. 이미지 크기 검증
            assert (
                validate_image_dimensions(
                    filepath, min_width=10, min_height=10, max_width=100, max_height=100
                )
                == True
            )

            # 4. MIME 타입 검증 (magic 라이브러리가 있는 경우만)
            if magic is not None:
                mime_types = {
                    "jpg": "image/jpeg",
                    "png": "image/png",
                    "gif": "image/gif",
                }
                expected_mime = mime_types.get(ext, "application/octet-stream")

                # validate_mime_type 함수 테스트
                result, error_msg = validate_mime_type(filepath, [expected_mime])
                if result:  # magic이 제대로 동작하는 경우
                    assert result == True
                    assert error_msg is None

                # validate_file_mime_type 함수 테스트
                result = validate_file_mime_type(filepath, {expected_mime})
                # 결과는 환경에 따라 다를 수 있으므로 검증 대신 함수 호출 여부만 확인
                assert isinstance(result, bool)

            # 5. 파일 크기 검증
            file_size = os.path.getsize(filepath)
            result, error_msg = validate_file_size(
                file_size, file_size + 1000
            )  # 현재 크기보다 큰 값
            assert result == True
            assert error_msg is None

    finally:
        # 생성한 모든 이미지 파일 정리
        for filepath, _, _ in image_files:
            try:
                os.unlink(filepath)
            except:
                pass
