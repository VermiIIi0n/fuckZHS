from unittest.mock import patch

from push import barkpusher, pushpluser


def test_pushplus_uses_https_timeout_and_query_params():
    with patch("push.requests.request") as request:
        pushpluser("title", "正文", "token")
    request.assert_called_once_with(
        "GET",
        "https://www.pushplus.plus/send",
        timeout=10,
        params={"token": "token", "title": "title", "content": "正文"},
    )


def test_bark_escapes_path_segments():
    with patch("push.requests.request") as request:
        barkpusher("标题", "a/b", "https://example.test/key/")
    request.assert_called_once_with(
        "GET",
        "https://example.test/key/%E6%A0%87%E9%A2%98/a%2Fb",
        timeout=10,
    )
