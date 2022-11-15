import requests


def pusher(title: str, content, token: str) -> None:
    requests.get(
        f"http://www.pushplus.plus/send?token={token}&title={title}&content={content}")
