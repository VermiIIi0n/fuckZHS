from unittest.mock import Mock, patch

from fucker import Fucker
from ObjDict import ObjDict
from zd_utils import Cipher


def test_dynamic_key_module_mapping():
    assert Fucker._dynamic_key_module("https://kg-ai-run.zhihuishu.com/run/gateway/t/stu/x") == 6
    assert Fucker._dynamic_key_module("https://studyservice-api.zhihuishu.com/gateway/t/v1/x") == 11
    assert Fucker._dynamic_key_module("https://example.test/api") is None


def test_zhidao_query_uses_dynamic_key_and_millisecond_timestamp():
    fucker = Fucker(proxies={"https": "http://proxy.invalid"})
    fucker._dynamic_keys = Mock()
    fucker._dynamic_keys.get.return_value = "0123456789abcdef"
    fucker._apiQuery = Mock(return_value=ObjDict({"code": 0}))

    with patch("fucker.time.time", return_value=1700000000.123):
        fucker.zhidaoQuery(
            "https://kg-ai-run.zhihuishu.com/run/gateway/t/stu/course-basic",
            {"title": "中文"},
        )

    call = fucker._apiQuery.call_args
    url = call.args[0]
    form = call.kwargs["data"]
    assert url.endswith("/course-basic")
    assert form["dateFormate"] == 1700000000123
    assert fucker._dynamic_keys.get.call_args.args == (6,)
    assert Cipher("0123456789abcdef").decrypt(form["secretStr"]).startswith(
        '{"title":"中文","dateFormate":1700000000123}'
    )
