from crm import utils


def test_short_id():
    assert utils.short_id("abcdef123456") == "abcdef12"


def test_safe_number():
    assert utils.safe_number("10") == 10.0
    assert utils.safe_number("x", default=5) == 5.0
