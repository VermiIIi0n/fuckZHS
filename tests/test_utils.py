import pytest

from utils import (
    list_to_cookie_jar,
    parse_bool,
    progressBar,
    versionCmp,
)


@pytest.mark.parametrize("value", [True, "1", "true", "YES", "on", " y "])
def test_parse_bool_true(value):
    assert parse_bool(value) is True


@pytest.mark.parametrize("value", [False, "0", "false", "NO", "off", " n "])
def test_parse_bool_false(value):
    assert parse_bool(value) is False


def test_parse_bool_rejects_unknown_value():
    with pytest.raises(ValueError):
        parse_bool("maybe")


@pytest.mark.parametrize(
    ("left", "right", "expected"),
    [("1.2.3", "1.2.3", 0), ("v2.0.0", "1.9.9", 1),
     ("1.2", "1.2.0", -1), ("2.0.0", "v2.0.0", 0),
     ("bad", "bad", 0)],
)
def test_version_cmp(left, right, expected):
    actual = versionCmp(left, right)
    assert (actual > 0) - (actual < 0) == expected


def test_progress_bar_handles_empty_total(capsys):
    assert progressBar(0, 0, progressbar_view=True) is False
    assert capsys.readouterr().out


def test_cookie_round_trip():
    jar = list_to_cookie_jar([{"name": "session", "value": "abc"}])
    assert jar.get("session") == "abc"
