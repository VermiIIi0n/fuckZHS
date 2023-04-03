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

def pushpluser(title: str, content, token: str) -> None:
    requests.get(
        f"http://www.pushplus.plus/send?token={token}&title={title}&content={content}")


def barkpusher(title: str, content, token: str) -> None:
    requests.get(
        f"{token}/{title}/{content}")
