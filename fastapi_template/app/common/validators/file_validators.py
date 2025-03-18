"""
# File: fastapi_template/app/common/validators/file_validators.py
# Description: 파일 검증 유틸리티 함수
"""

import os
import imghdr
from typing import List, Optional, Set, Tuple

# python-magic 라이브러리 사용 (pip install python-magic 필요)
# Windows에서는 pip install python-magic-bin 설치 필요
try:
    import magic
except ImportError:
    magic = None


def validate_file_extension(
    filename: str, allowed_extensions: Set[str]
) -> Tuple[bool, Optional[str]]:
    """
    파일 확장자가 허용된 목록에 있는지 검증합니다.

    Args:
        filename: 검증할 파일명
        allowed_extensions: 허용된 확장자 집합 (예: {'.jpg', '.png'})

    Returns:
        tuple[bool, Optional[str]]: (검증 결과, 실패 시 오류 메시지)
    """
    _, ext = os.path.splitext(filename)
    ext = ext.lower()

    if ext not in allowed_extensions:
        return (
            False,
            f"파일 확장자 '{ext}'은(는) 허용되지 않습니다. 허용된 확장자: {', '.join(allowed_extensions)}",
        )

    return True, None


def validate_file_size(
    file_size: int, max_size_bytes: int
) -> Tuple[bool, Optional[str]]:
    """
    파일 크기가 최대 허용 크기 이하인지 검증합니다.

    Args:
        file_size: 파일 크기 (바이트)
        max_size_bytes: 최대 허용 파일 크기 (바이트)

    Returns:
        tuple[bool, Optional[str]]: (검증 결과, 실패 시 오류 메시지)
    """
    if file_size > max_size_bytes:
        # 사용자 친화적인 크기 표시
        if max_size_bytes < 1024:
            size_str = f"{max_size_bytes} bytes"
        elif max_size_bytes < 1024 * 1024:
            size_str = f"{max_size_bytes / 1024:.1f} KB"
        else:
            size_str = f"{max_size_bytes / (1024 * 1024):.1f} MB"

        return (
            False,
            f"파일 크기({file_size / (1024 * 1024):.1f} MB)가 최대 허용 크기({size_str})를 초과합니다.",
        )

    return True, None


def validate_image_file(file_path: str) -> Tuple[bool, Optional[str]]:
    """
    파일이 유효한 이미지 파일인지 검증합니다.

    Args:
        file_path: 이미지 파일 경로

    Returns:
        tuple[bool, Optional[str]]: (검증 결과, 실패 시 오류 메시지)
    """
    # 파일 확장자 검사
    _, ext = os.path.splitext(file_path)
    ext = ext.lower()
    allowed_exts = {".jpg", ".jpeg", ".png", ".gif", ".bmp", ".webp"}

    if ext not in allowed_exts:
        return (
            False,
            f"'{ext}' 확장자는 허용된 이미지 형식이 아닙니다. 허용된 형식: {', '.join(allowed_exts)}",
        )

    # 실제 이미지 파일인지 내용 기반 검사
    try:
        img_type = imghdr.what(file_path)
        if img_type is None:
            return False, "파일 내용이 이미지 형식이 아닙니다."
    except Exception as e:
        return False, f"이미지 파일 검증 중 오류 발생: {str(e)}"

    return True, None


def validate_mime_type(
    file_path: str, allowed_mime_types: List[str]
) -> Tuple[bool, Optional[str]]:
    """
    파일의 MIME 타입이 허용된 목록에 있는지 검증합니다.

    Args:
        file_path: 파일 경로
        allowed_mime_types: 허용된 MIME 타입 목록

    Returns:
        tuple[bool, Optional[str]]: (검증 결과, 실패 시 오류 메시지)
    """
    if magic is None:
        return (
            False,
            "python-magic 라이브러리가 설치되지 않았습니다. 'pip install python-magic' 또는 'pip install python-magic-bin'(Windows)을 실행하세요.",
        )

    try:
        # python-magic 라이브러리 사용
        mime_type = magic.from_file(file_path, mime=True)

        if mime_type not in allowed_mime_types:
            return (
                False,
                f"파일 타입({mime_type})은 허용되지 않습니다. 허용된 타입: {', '.join(allowed_mime_types)}",
            )

        return True, None
    except Exception as e:
        return False, f"MIME 타입 검증 중 오류 발생: {str(e)}"
