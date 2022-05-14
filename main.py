import os
import re
import json
import argparse
import requests
from fucker import Fucker
from logger import logger
from ObjDict import ObjDict
from utils import getConfigPath, getRealPath, versionCmp

DEFAULT_CONFIG = {
    "username": "",
    "password": "",
    "proxies": {},
    "logLevel": "INFO"
}
# get config or create one if not exist
if os.path.isfile(getConfigPath()):
    with open(getConfigPath(), 'r') as f:
        config = ObjDict(json.load(f))
else:
    config = ObjDict(DEFAULT_CONFIG)
    with open(getConfigPath(), 'w') as f:
        json.dump(config, f, indent=4)

# parse auguments
parser = argparse.ArgumentParser(prog="ZHS Fucker")
parser.add_argument("-c", "--course", type=str, nargs="+", help="CourseId or recruitAndCourseId, can be found in URL")
parser.add_argument("-v", "--videos", type=str, nargs="+", help="Video IDs(fileId), can be found in URL, won't work if -c is recruitAndCourseId")
parser.add_argument("-u", "--username", type=str, help="if not set anywhere, will be prompted")
parser.add_argument("-p", "--password", type=str, help="If not set anywhere, will be prompted. Be careful, it will be stored in history")
parser.add_argument("-s", "--speed", type=float, help="Video Play Speed, default value is maximum speed when watching in browser")
parser.add_argument("-t", "--threshold", type=float, help="Video End Threshold, above this will be considered finished, overloaded when there are questions left unanswered")
parser.add_argument("-l", "--limit", type=int, help="Time Limit (in minutes, 0 for no limit), default is 0")
parser.add_argument("-d", "--debug", action="store_true", help="Debug Mode")
parser.add_argument("--proxy", type=str, help="HTTP Proxy Server, e.g: http://127.0.0.1:8080")

args = parser.parse_args()

course = args.course
while not course:
    course = [input("Requires courseId or recruitAndCourseId: ")]
username = args.username or config.username
password = args.password or config.password
logger.setLevel("DEBUG" if args.debug else config.logLevel)
proxies = config.proxies

if logger.getLevel() == "DEBUG":
    print("*****************************\n"+
          "DEBUG MODE ENABLED\n"+
          "SENSITIVE DATA WILL BE LOGGED\n"+
          "*****************************\n")

if args.proxy: # parse proxy
    scheme = re.search(r"^(\w+)://", args.proxy.strip())
    if scheme is None:
        raise ValueError("Invalid proxy, can't parse scheme")
    scheme = scheme.group(1).lower()
    match scheme:
        case "http"|"https":
            proxies["http"] = args.proxy
            proxies["https"] = args.proxy
        case "socks4":
            proxies["socks4"] = args.proxy
        case "socks5":
            proxies["socks5"] = args.proxy
        case _:
            raise ValueError("Unsupported proxy type")

# check update
with open(getRealPath("meta.json"), "r") as f:
    try: # some exceptions won't be caught by 'with'
        m = ObjDict(json.load(f))
        url = f"https://raw.githubusercontent.com/{m.author}/fuckZHS/{m.branch}/meta.json"
        r = ObjDict(requests.get(url, proxies=proxies, timeout=5).json())
        current = m.version
        latest = r.version
        if versionCmp(current, latest) < 0:
            print("*********************************\n"+
                 f"New version available: {latest}\n"+
                 f"Current version: {current}\n"+
                  "*********************************\n")
    except Exception:
        pass

### create an instance, now we are talking... or fucking
fucker = Fucker(proxies=proxies, speed=args.speed, end_thre=args.threshold, limit=args.limit or 0)

### first you need to login to get cookies
fucker.login(username, password)

# you can add cookies manually by setting cookies property of a Fucker instance
# notice that cookies of zhihuishu.com expires if you login again in somewhere else
# fucker.cookies = {}

# auto detect mode
for c in course:
    if args.videos:
        for v in args.videos:
            try:
                fucker.fuckVideo(course_id=c, video_id=v)
                print(f"fucked {v}")
                args.videos.remove(v)
            except Exception:
                pass
    else:
        fucker.fuckCourse(course_id=c)
if args.videos:
    print(f"the following videos are not fucked: {args.videos}")
    
## use fuckCourse method to fuck the entire course
# fucker.fuckCourse(course_id="")

## or if you want to fuck a video, use fuckVideo method
# fucker.fuckVideo(course_id="", file_id="")

# check the source code or README to find more info
