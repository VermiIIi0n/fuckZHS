import os
import json
import argparse
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

# parse auguments
parser = argparse.ArgumentParser(prog="ZHS Fucker")
parser.add_argument("-c", "--course", type=str, required=True, help="Course ID, can be found in URL")
parser.add_argument("-v", "--videos", type=str, nargs="+", help="Video IDs, can be found in URL")
parser.add_argument("-u", "--username", type=str)
parser.add_argument("-p", "--password", type=str)
parser.add_argument("-s", "--speed", type=float, help="Video Play Speed")
parser.add_argument("-t", "--threshold", type=float, help="Video End Threshold")
parser.add_argument("--webdriver", type=str, help="WebDriver Executable Path")

args = parser.parse_args()

username = args.username or config.username
password = args.password or config.password
webdriver_path = args.webdriver or config.webdriverPath

webdriver_opts = {}
if webdriver_path:
    webdriver_path = getRealPath(webdriver_path)
    webdriver_opts.update({"executable_path": webdriver_path}) # deprecated warning, I didn't bother to fix it

fucker = Fucker(webdriver_opts=webdriver_opts, speed=args.speed, end_thre=args.threshold) # create an instance, now we are talking... or fucking

# first you need to login to get cookies
fucker.login(username, password)
# if you cannot use selenium, you can add cookies manually by setting cookies property of Fucker
# notice that cookies of zhihuishu.com expires if you login again in other browser session
# fucker.cookies = {}

# auto detect mode
if args.videos:
    for v in args.videos:
        print(f"fucking {v}")
        fucker.fuckVideo(course_id=args.course, file_id=v)
else:
    fucker.fuckCourse(course_id=args.course)
# now you can user fuckCourse method to fuck the entire course
# fucker.fuckCourse(course_id="")
# or if you want to fuck a video, you can use fuckVideo method
# fucker.fuckVideo(course_id="", file_id="")

# check the source code or README to find more info
