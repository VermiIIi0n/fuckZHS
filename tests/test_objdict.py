import pytest

from ObjDict import ObjDict


def test_nested_attribute_access_and_default():
    value = ObjDict({"user": {"name": "Ada"}}, default=None)
    assert value.user.name == "Ada"
    assert value.missing is None


def test_missing_key_raises_when_no_default():
    value = ObjDict({})
    with pytest.raises(KeyError):
        _ = value["missing"]


def test_copy_is_shallow():
    original = ObjDict({"nested": {"value": 1}})
    copied = original.copy()
    assert copied == original
    assert copied is not original
    assert copied.nested is original.nested
