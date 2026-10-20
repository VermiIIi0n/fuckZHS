'''
Author: Vincent Young, jiajiu123
Date: 2023-03-30 00:15:22
LastEditors: Vincent Young
LastEditTime: 2023-03-30 02:40:33
FilePath: /fuckZHS/push.py
Telegram: https://t.me/missuo(Vincent Young)

Copyright © 2023 by Vincent, All Rights Reserved. 
'''
import requests
from urllib.parse import quote


def _request(method: str, url: str, **kwargs):
    """Send a notification without allowing a provider outage to stop a run."""
    try:
        return requests.request(method, url, timeout=10, **kwargs)
    except requests.RequestException:
        return None

def pushpluser(title: str, content, token: str) -> None:
    _request(
        "GET",
        "https://www.pushplus.plus/send",
        params={"token": token, "title": title, "content": str(content)},
    )


def barkpusher(title: str, content, token: str) -> None:
    url = f"{token.rstrip('/')}/{quote(str(title), safe='')}/{quote(str(content), safe='')}"
    _request("GET", url)
