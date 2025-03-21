import pytest
from app.common.validators.string_validators import (
    validate_email,
    validate_url,
    validate_korean_name,
    validate_password,
    validate_password_strength,
    validate_phone_number,
)


def test_validate_email():
    # 유효한 이메일 테스트
    assert validate_email("user@example.com") == True

    # 유효하지 않은 이메일 테스트
    assert validate_email("invalid_email") == False
    assert validate_email("user@example") == False


@pytest.mark.parametrize(
    "email,expected",
    [
        ("user@example.com", True),
        ("user.name@example.co.kr", True),
        ("user+tag@example.com", True),
        ("invalid_email", False),
        ("missing_domain@", False),
        ("@missing_username.com", False),
        ("no_at_sign.com", False),
        ("double@@at.com", False),
    ],
)
def test_validate_email_multiple_cases(email, expected):
    assert validate_email(email) == expected


def test_validate_url():
    # 유효한 URL 테스트
    assert validate_url("https://example.com") == True
    assert validate_url("http://sub.example.co.kr/path?query=123") == True

    # 유효하지 않은 URL 테스트
    assert validate_url("not-a-url") == False

    # HTTPS 필수 옵션 테스트
    assert validate_url("http://example.com", require_https=True) == False
    assert validate_url("https://example.com", require_https=True) == True


def test_validate_korean_name():
    # 유효한 한국어 이름 테스트
    assert validate_korean_name("홍길동") == True
    assert validate_korean_name("김철수") == True

    # 유효하지 않은 한국어 이름 테스트
    assert validate_korean_name("Hong") == False  # 영문
    assert validate_korean_name("홍길동123") == False  # 숫자 포함
    assert validate_korean_name("홍") == False  # 한 글자
    assert validate_korean_name("홍길동이박사") == False  # 6글자


def test_validate_password():
    # 기본 설정으로 테스트
    assert validate_password("Abcd1234!") == True

    # 조건 미충족 테스트
    assert validate_password("abcd1234") == False  # 대문자 없음
    assert validate_password("ABCD1234!") == False  # 소문자 없음
    assert validate_password("Abcdefgh!") == False  # 숫자 없음
    assert validate_password("Abcd1234") == False  # 특수문자 없음
    assert validate_password("A1!") == False  # 최소 길이 미달

    # 커스텀 설정 테스트
    assert (
        validate_password("abcd1234", require_uppercase=False) == False
    )  # 특수문자 없음
    assert (
        validate_password(
            "abcd!", min_length=5, require_uppercase=False, require_digit=False
        )
        == True
    )


def test_validate_password_strength():
    # 유효한 비밀번호 테스트
    result, msg = validate_password_strength("StrongPwd1!")
    assert result == True
    assert msg is None

    # 길이 검증 테스트
    result, msg = validate_password_strength("Weak1!")
    assert result == False
    assert msg is not None
    assert "최소" in str(msg)
    assert "8자" in str(msg)

    # 대문자 검증 테스트
    result, msg = validate_password_strength("weakpwd1!")
    assert result == False
    assert msg is not None
    assert "대문자" in str(msg)

    # 소문자 검증 테스트
    result, msg = validate_password_strength("STRONGPWD1!")
    assert result == False
    assert msg is not None
    assert "소문자" in str(msg)

    # 숫자 검증 테스트
    result, msg = validate_password_strength("StrongPwd!")
    assert result == False
    assert msg is not None
    assert "숫자" in str(msg)

    # 특수문자 검증 테스트
    result, msg = validate_password_strength("StrongPwd1")
    assert result == False
    assert msg is not None
    assert "특수문자" in str(msg)

    # 커스텀 설정 테스트
    result, msg = validate_password_strength(
        "simple",
        min_length=6,
        require_uppercase=False,
        require_lowercase=True,
        require_digits=False,
        require_special_chars=False,
    )
    assert result == True
    assert msg is None


def test_validate_phone_number():
    # 유효한 한국 휴대폰 번호 테스트
    assert validate_phone_number("01012345678") == True
    assert validate_phone_number("01098765432") == True
    assert validate_phone_number("0109876543") == True  # 7자리 국번

    # 유효하지 않은 한국 휴대폰 번호 테스트
    assert validate_phone_number("01234567890") == False  # 올바르지 않은 형식
    assert validate_phone_number("0212345678") == False  # 유선전화 형식

    # 미국 전화번호 테스트
    assert validate_phone_number("1234567890", country_code="US") == True
    assert validate_phone_number("123.456.7890", country_code="US") == True
    assert validate_phone_number("123-456-7890", country_code="US") == True

    # 유효하지 않은 미국 전화번호 테스트
    assert validate_phone_number("12345", country_code="US") == False

    # 지원하지 않는 국가 코드 테스트
    with pytest.raises(ValueError):
        validate_phone_number("12345678", country_code="XX")
