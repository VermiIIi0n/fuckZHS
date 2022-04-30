import os
import json
from fucker import Fucker
from logger import logger
from utils import ObjDict, getConfigPath, getRealPath

DEFAULT_CONFIG = {
    "username": "",
    "password": "",
    "webdriverPath": None,
    "logLevel": "INFO"
}
# get config or create one if not exist
if os.path.isfile(getConfigPath()):
    with open(getConfigPath(), 'r') as f:
        config = ObjDict(json.load(f))
else:
    config = ObjDict(DEFAULT_CONFIG)
    with open(getConfigPath(), 'w') as f:
        json.dump(config, f)

logger.setLevel(config.logLevel)

username = config.username
password = config.password

webdriver_path = config.get("webdriverPath", None)
webdriver_opts = {}
if webdriver_path:
    webdriver_path = getRealPath(webdriver_path)
    webdriver_opts.update({"executable_path": webdriver_path})

fucker = Fucker(webdriver_opts=webdriver_opts) # create an instance, now we are talking... or fucking

# first you need to login to get cookies
fucker.login(username, password)
# if you cannot use selenium, you can add cookies manually by setting cookies property of Fucker
# notice that cookies of zhihuishu.com expires if you login again in other browser session
# fucker.cookies = {}

# now if you want to fuck a course, use fuckCourse method
fucker.fuckCourse(course_id="")

# or if you want to fuck a video, you can use fuckVideo method
# fucker.fuckVideo(course_id="", file_id="")

# check the source code or README to find more info
