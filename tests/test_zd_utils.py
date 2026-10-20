import pytest

from unittest.mock import Mock, patch

from zd_utils import Cipher, DynamicKeyCache, fetch_dynamic_key


@pytest.mark.parametrize("value", ["", "ascii", "你好，世界", "😀" * 17])
def test_cipher_round_trip_supports_utf8(value):
    encrypted = Cipher().encrypt(value)
    assert Cipher().decrypt(encrypted) == value


def test_cipher_rejects_invalid_padding():
    with pytest.raises(ValueError):
        Cipher.unpad(b"not-a-valid-block")


def test_dynamic_key_cache_reuses_key():
    with patch("zd_utils.fetch_dynamic_key", return_value="0123456789abcdef") as fetch:
        cache = DynamicKeyCache(session=Mock(), ttl=300)
        assert cache.get(6) == "0123456789abcdef"
        assert cache.get(6) == "0123456789abcdef"
    fetch.assert_called_once_with(6, cache.session, None)


def test_fetch_dynamic_key_uses_module_endpoint_and_payload():
    response = Mock()
    response.json.return_value = {"rt": {"sl": "ciphertext"}}
    response.raise_for_status.return_value = None
    session = Mock()
    session.get.return_value = response
    with patch("zd_utils._rsa_public_decrypt", return_value={"cKey": "0123456789abcdef"}) as decrypt:
        assert fetch_dynamic_key(6, session=session) == "0123456789abcdef"
    request = session.get.call_args
    assert request.args[0].endswith("/c/has")
    assert request.kwargs["timeout"] == 10
    assert set(request.kwargs["params"]) == {"uid"}
    decrypt.assert_called_once_with("ciphertext")
