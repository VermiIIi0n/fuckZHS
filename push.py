import requests
token = ""
def pusher(title,content):
    requests.get(f"http://www.pushplus.plus/send?token={token}&title={title}&content={content}")