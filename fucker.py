from zd_utils import Cipher, getEv, WatchPoint, HOME_KEY, VIDEO_KEY, QA_KEY, AI_KEY, EXAM_KEY
from utils import progressBar, HMS, wipeLine, list_to_cookie_jar, getRealPath
from urllib.parse import unquote_plus as unquote
from requests.adapters import HTTPAdapter, Retry
from requests.cookies import RequestsCookieJar
from requests.utils import cookiejar_from_dict
from base64 import b64encode, b64decode
from random import randint, random, uniform, sample
from random import choice as random_choice
from datetime import datetime
from functools import partial
from threading import Thread
from getpass import getpass
from ObjDict import ObjDict
from logger import logger
from push import pushpluser
from push import barkpusher
from sign import sign
import urllib.request
import requests
import math
import time
import json
import re
import os
from urllib.parse import urlparse
from urllib.parse import urlencode, parse_qsl, urlsplit, urlunsplit
from pathlib import Path
from openai import OpenAI
import threading
import ast
import hashlib
import string
import tiktoken

"""
⠄⠄⠄⢰⣧⣼⣯⠄⣸⣠⣶⣶⣦⣾⠄⠄⠄⠄⡀⠄⢀⣿⣿⠄⠄⠄⢸⡇⠄⠄
⠄⠄⠄⣾⣿⠿⠿⠶⠿⢿⣿⣿⣿⣿⣦⣤⣄⢀⡅⢠⣾⣛⡉⠄⠄⠄⠸⢀⣿⠄
⠄⠄⢀⡋⣡⣴⣶⣶⡀⠄⠄⠙⢿⣿⣿⣿⣿⣿⣴⣿⣿⣿⢃⣤⣄⣀⣥⣿⣿⠄
⠄⠄⢸⣇⠻⣿⣿⣿⣧⣀⢀⣠⡌⢻⣿⣿⣿⣿⣿⣿⣿⣿⣿⠿⠿⠿⣿⣿⣿⠄
⠄⢀⢸⣿⣷⣤⣤⣤⣬⣙⣛⢿⣿⣿⣿⣿⣿⣿⡿⣿⣿⡍⠄⠄⢀⣤⣄⠉⠋⣰
⠄⣼⣖⣿⣿⣿⣿⣿⣿⣿⣿⣿⢿⣿⣿⣿⣿⣿⢇⣿⣿⡷⠶⠶⢿⣿⣿⠇⢀⣤
⠘⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣽⣿⣿⣿⡇⣿⣿⣿⣿⣿⣿⣷⣶⣥⣴⣿⡗
⢀⠈⢿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⡟⠄
⢸⣿⣦⣌⣛⣻⣿⣿⣧⠙⠛⠛⡭⠅⠒⠦⠭⣭⡻⣿⣿⣿⣿⣿⣿⣿⣿⡿⠃⠄
⠘⣿⣿⣿⣿⣿⣿⣿⣿⡆⠄⠄⠄⠄⠄⠄⠄⠄⠹⠈⢋⣽⣿⣿⣿⣿⣵⣾⠃⠄
⠄⠘⣿⣿⣿⣿⣿⣿⣿⣿⠄⣴⣿⣶⣄⠄⣴⣶⠄⢀⣾⣿⣿⣿⣿⣿⣿⠃⠄⠄
⠄⠄⠈⠻⣿⣿⣿⣿⣿⣿⡄⢻⣿⣿⣿⠄⣿⣿⡀⣾⣿⣿⣿⣿⣛⠛⠁⠄⠄⠄
⠄⠄⠄⠄⠈⠛⢿⣿⣿⣿⠁⠞⢿⣿⣿⡄⢿⣿⡇⣸⣿⣿⠿⠛⠁⠄⠄⠄⠄⠄
⠄⠄⠄⠄⠄⠄⠄⠉⠻⣿⣿⣾⣦⡙⠻⣷⣾⣿⠃⠿⠋⠁⠄⠄⠄⠄⠄⢀⣠⣴
⣿⣿⣿⣶⣶⣮⣥⣒⠲⢮⣝⡿⣿⣿⡆⣿⡿⠃⠄⠄⠄⠄⠄⠄⠄⣠⣴⣿⣿⣿
"""

SMART_BASE = "https://kg-ai-run.zhihuishu.com/run/gateway/t/stu"   # 智慧课程 API 网关
SMART_REPORT_INTERVAL = 10  # 智慧课程视频进度上报间隔（秒）
SMART_DEFAULT_SPEED = 60.0  # 智慧课程视频默认倍速（40x~100x 实测均 100% 被接受，取 60x 留余量）
SMART_MAX_SPEED = 100.0     # 智慧课程视频倍速上限，再高收益有限且更容易被风控
SMART_EXAM_MAX_ATTEMPTS = 6  # 知识点练习单次运行最多尝试次数（题库较大时需要多轮才能刷满）
SMART_EXAM_TARGET = 95       # 掌握度目标，达到后不再练习
SMART_EXAM_BASE = "https://studentexamtest.zhihuishu.com/gateway/t/v1"  # 智慧课程练习/考试网关


def smartInt(v):
    """智慧课程接口里的 id 有时是数字有时是字符串，尽量转成 int"""
    try:
        return int(v)
    except (TypeError, ValueError):
        return v


class TimeLimitExceeded(TimeoutError):
    pass

class CaptchaException(Exception):
    pass

class Fucker:
    def __init__(self, cookies: dict = None,
                 headers: dict = None,
                 proxies: dict = None,
                 limit: int = 0,
                 speed: float = None,
                 end_thre: float = None,
                 pushplus_token: str = '',
                 bark_token: str = '',
                 tree_view:bool = True,
                 progressbar_view:bool = True,
                 image_path:str = ""):
        """
        ### Fucker Class
        * `cookies`: dict, optional, cookies to use for the session
        * `headers`: dict, optional, headers to use for the session
        * `proxies`: dict, optional, proxies to use for the session
        * `limit`: int, optional, time limit for each course, in minutes (default is 0), auto resets on fuck*Course methods call
        * `speed`: float, optional, video playback speed
        * `end_thre`: float, optional, threshold to stop the fucker, overloaded when there are questions left unanswered
        * `tree_view` :bool, optional, print the tree progress view of the course
        """
        logger.debug(f"created a Fucker {id(self)}, limit: {limit}, speed: {speed}, end_thre: {end_thre}")

        self.uuid = None # actually it's not a uuid, but a random string
        self.cookies = cookies or {}
        self.proxies = proxies or urllib.request.getproxies() # explicitly use system proxy
        self.headers = headers or {
            "Accept": "*/*",
            "sec-ch-ua": "\" Not A;Brand\";v=\"99\", \"Chromium\";v=\"101\", \"Google Chrome\";v=\"101\"",
            "sec-ch-ua-mobile": "?0",
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/100.0.4896.127 Safari/537.36",
            "sec-ch-ua-platform": "macOS",
            "Accept-Encoding": "gzip, deflate, br",
            "Accept-Language": "en-GB,en;q=0.9"
        }
        retry = Retry(total=5,
                      backoff_factor=0.1, 
                      raise_on_status=True,
                      status_forcelist=[500, 502, 503, 504])
        self.session = requests.Session()
        self.session.mount('http://', HTTPAdapter(max_retries=retry))
        self.session.mount('https://', HTTPAdapter(max_retries=retry))

        logger.debug(f'proxies: {self.proxies}')
        logger.debug(f'headers: {self.headers}')

        self.limit = abs(limit)                    # time limit for fucking, in minutes
        self.speed = speed and max(speed, 0.1)     # video play speed, Falsy values for default
        self.end_thre = max(end_thre or 0, 0.0) or 0.91 # video play end threshold, above this will be considered as finished
        self.prefix = "  |"                        # prefix for tree view
        self.context = ObjDict(default=None)       # context for methods
        self.courses = ObjDict(default=None)       # store courses info
        self._pushplus = partial(pushpluser, token=pushplus_token) if pushplus_token else lambda *args, **kwargs: None
        self._bark = partial(barkpusher, token=bark_token) if bark_token else lambda *args, **kwargs: None
        self.tree_view = tree_view
        self.progressbar_view = progressbar_view
        self.image_path = image_path

    @property # cannot directly manipulate _cookies property, we need to parse uuid from cookies
    def cookies(self) -> RequestsCookieJar:
        return self._cookies

    @cookies.setter
    def cookies(self, cookies: dict | list | RequestsCookieJar):
        if isinstance(cookies, dict):
            cookies = cookiejar_from_dict(cookies)
        elif isinstance(cookies, list):
            cookies = list_to_cookie_jar(cookies)
        
        self._cookies = cookies
        logger.debug(f'received cookies: {self.cookies}')
        if cookies:
            try:
                self.uuid = json.loads(unquote(cookies["CASLOGC"]))["uuid"]
                self._cookies[f"exitRecod_{self.uuid}"] = "2"
            except KeyError:
                raise ValueError("Cookies invalid")
        logger.debug(f"set cookies: {self._cookies}")

    def login(self, username: str=None, password: str=None, interactive: bool=True, use_qr:bool=False, qr_callback: callable=None):
        """* `interactive`: whether to use interactive mode to login"""
        if use_qr:
            if not callable(qr_callback):
                raise ValueError("callable qr_callback is required when use_qr is True")
            self._qrlogin(qr_callback)
            return
        while not username or not password:
            if not interactive:
                raise ValueError("username or password being empty")
            if not username:
                username = input("Username: ")
            else:
                print(f"Username: {username}")
            if not password:
                password = getpass("Password: ")
        # urls
        login_page = "https://passport.zhihuishu.com/login?service=https://onlineservice-api.zhihuishu.com/login/gologin"
        valid_url = "https://passport.zhihuishu.com/user/validateAccountAndPassword"
        check_url = "https://appcomm-user.zhihuishu.com/app-commserv-user/userInfo/checkNeedAuth"
        self._sessionReady() # set cookies, headers, proxies
        self.session.headers.update({
            "Origin": "https://passport.zhihuishu.com",
            "Referer": login_page
        })
        try:
            self.session.get(login_page, proxies=self.proxies, timeout=10)
            form = {
                "account": username,
                "password": password
            }
            user_info = self._apiQuery(valid_url, form) # get uuid and pwd
            match user_info.status:
                case 1:
                    pass # success
                case -2:
                    raise ValueError("Username or password invalid")
                case -4:
                    raise Exception("Multiple invalid attempts, requires captcha")
                case -9:
                    raise Exception("Account requires SMS verification")
                case _:
                    pass # unknown error, just try to ignore
            need_auth = self._apiQuery(check_url, {"uuid": user_info.uuid}).rt.needAuth
            if need_auth:
                raise Exception("Account need auth, please login using browser to pass auth")
            params = {"account":username,
                      "pwd": user_info.pwd,
                      "validate": 0
                    }
            self.session.get(login_page, params=params, proxies=self.proxies, timeout=10)
            self.cookies = self.session.cookies.copy()
            if not self.cookies:
                raise Exception("No cookies found")

            logger.info("Login successful")
        except Exception as e:
            logger.exception(e)
            raise Exception(f"Login failed: {e}")

    def _qrlogin(self, qr_callback):
        """Login using qr code"""
        login_page = "https://passport.zhihuishu.com/login?service=https://onlineservice-api.zhihuishu.com/login/gologin"
        qr_page = "https://passport.zhihuishu.com/qrCodeLogin/getLoginQrImg"
        query_page = "https://passport.zhihuishu.com/qrCodeLogin/getLoginQrInfo"
        self._sessionReady()
        try:
            r = self.session.get(qr_page, timeout=10).json()
            qrToken = r["qrToken"]
            img = b64decode(r["img"])
            if self.image_path != "": # 路径非空时保存图片到指定路径
                image_path = f"{os.path.join(self.image_path, time.strftime('%Y-%m-%dT%H-%M-%S'))}.png"
                with open(image_path, "wb") as f:
                    f.write(img)
                logger.info(f"图片已保存至{image_path}")
            qr_callback(img)
            logger.debug(f"QR login received, token{qrToken}")
            scanned = False
            while True:
                time.sleep(0.5)
                msg = ObjDict(
                    self.session.get(query_page, params={"qrToken":qrToken}, timeout=10).json(),
                    default=None)
                match msg.status:
                    case -1:
                        pass # not scanned
                    case 0:
                        if not scanned:
                            scanned = True
                            logger.info(f"QR Scanned: {msg.msg}")
                            print("QR Scanned")
                    case 1:
                        logger.info(f"One-time code get: {msg.msg}")
                        print("One-time code received")
                        self.session.get(login_page, params={"pwd":msg.oncePassword}, proxies=self.proxies, timeout=10)
                        self.cookies = self.session.cookies.copy()
                        if not self.cookies:
                            raise Exception("No cookies found")
                        logger.info("Login successful")
                        break
                    case 2:
                        print("QR code expired")
                        raise TimeLimitExceeded(f"QR code expired: {msg.msg}")
                    case 3:
                        raise Exception(f"Login canceled")
                    case _:
                        raise Exception(f"Unknown Response {msg.msg}")

        except TimeLimitExceeded:
            self._qrlogin(qr_callback) # timeout? try again!
        except Exception as e:
            logger.exception(e)
            raise Exception(f"QR login failed: {e}")

#    def _qrlogin(self, qr_callback):
#        """Login using qr code"""
#        login_page = "https://passport.zhihuishu.com/login?service=https://onlineservice-api.zhihuishu.com/login/gologin"
#        qr_page = "https://passport.zhihuishu.com/qrCodeLogin/getLoginQrImg"
#        self._sessionReady()
#        async def wait(url):
#            async with websockets.connect(url, extra_headers=self.headers) as websocket:
#                while True:
#                    msg = await websocket.recv()
#                    msg = ObjDict(json.loads(msg), default=None)
#                    logger.debug(f"QR login received {msg}")
#                    match msg.code:
#                        case 0:
#                            logger.info(f"QR Scanned: {msg.msg}")
#                            print("QR Scanned")
#                        case 1:
#                            logger.info(f"One-time code get: {msg.msg}")
#                            print("One-time code received")
#                            self.session.get(login_page, params={"pwd":msg.oncePassword}, proxies=self.proxies, timeout=10)
#                            self.cookies = self.session.cookies.copy()
#                            if not self.cookies:
#                                raise Exception("No cookies found")
#                            logger.info("Login successful")
#                            break
#                        case 2:
#                            print("QR code expired")
#                            raise TimeLimitExceeded(f"QR code expired: {msg.msg}")
#                        case 3:
#                            raise Exception(f"Login canceled")
#                        case _:
#                            raise Exception(f"Unknown Response {msg.msg}")
#        try:
#            r = self.session.get(qr_page, timeout=10).json()
#            qrToken = r["qrToken"]
#            img = b64decode(r["img"])
#            qr_callback(img)
#            logger.debug("Start QR login WebSocket")
#            asyncio.run(wait(f"wss://appcomm-user.zhihuishu.com/app-commserv-user/websocket?qrToken={qrToken}"))
#        except TimeLimitExceeded:
#            self._qrlogin(qr_callback) # timeout? try again!
#        except Exception as e:
#            logger.exception(e)
#            raise Exception(f"QR login failed: {e}")

    def getSmartCourseListSafe(self):
        """### 取得智慧课程列表，失败时返回空列表（不影响其它课程类型，且不重复重试）"""
        if getattr(self, "_smartListBroken", False):
            return []
        try:
            return self.getSmartCourseList() or []
        except Exception as e:
            self._smartListBroken = True
            logger.error(f"Failed to get smart course list: {e}")
            return []

    def findSmartCourse(self, course_id):
        """### 按 courseId 在智慧课程列表里找课程"""
        for c in self.getSmartCourseListSafe():
            if str(c.get("courseId")) == str(course_id):
                return c
        return None

    def fuckWhatever(self):
        """Fuck whatever is found"""
        zhidao_ids = [c.secret for c in self.getZhidaoList()]
        for i in zhidao_ids:
            try:
                self.fuckZhidaoCourse(i)
            except Exception as e:
                logger.exception(e)
                continue
        hike_ids = [c.courseId for c in self.getHikeList()]
        for i in hike_ids:
            try:
                self.fuckHikeCourse(i)
            except Exception as e:
                logger.exception(e)
                continue
        # 智慧课程（新形态课程），courseId/classId 都在课程列表里
        for c in self.getSmartCourseListSafe():
            try:
                self.fuckSmartCourse(c.courseId, c.classId)
            except Exception as e:
                logger.exception(e)
                continue

    def fuckCourse(self, course_id:str):
        """
        ### Fuck the whole course
        * `course_id`: `courseId`(Hike/Smart) or `recuitAndCourseId`(Zhidao)
        """
        if re.match(r".*[a-zA-Z].*", course_id): # determine if it's a courseId or a recruitAndCourseId
            self.fuckZhidaoCourse(course_id) # it's a recruitAndCourseId
        else: # it's a courseId
            smart = self.findSmartCourse(course_id)
            if smart: # it's a smart course
                self.fuckSmartCourse(smart.courseId, smart.classId)
            else: # it's a hike courseId
                self.fuckHikeCourse(course_id)

    def fuckVideo(self, course_id, video_id:str):
        """
        ### Fuck a single video
        * `course_id`: `courseId`(Hike) or `recuitAndCourseId`(Zhidao)
        * `video_id`: `fileId`(Hike) or `videoId`(Zhidao, not visible in URL)
        """
        if re.match(r".*[a-zA-Z].*", course_id):
            self.fuckZhidaoVideo(course_id, video_id)
        else:
            self.fuckHikeVideo(course_id, video_id)

#############################################
# for some fucking reasons
# there are 2 sets of completely different API for hike.zhihuishu.com and studyservice-api.zhihuishu.com
# so we need to use different methods for different API
#############################################
# following are methods for studyservice-api.zhihuishu.com API
    def getZhidaoList(self):
        """
        ### Get all courses of zhidao from server
        """
        if self.courses.zhidao:
            return self.courses.zhidao
        url = "https://onlineservice-api.zhihuishu.com/gateway/t/v1/student/course/share/queryShareCourseInfo"
        self._checkCookies()
        self._sessionReady()
        page = 1 # initial page number
        data = {"status": 0, "pageNo": page, "pageSize": 5}
        r = self.zhidaoQuery(url, data, ok_code=200, key=HOME_KEY).result
        r.default = None
        total = r.totalCount or 0
        self.courses.zhidao = r.courseOpenDtos or []
        for i in range(2, int(math.ceil(total/5))+1):
            data["pageNo"] = i
            r = self.zhidaoQuery(url, data, ok_code=200, key=HOME_KEY).result
            self.courses.zhidao += r.courseOpenDtos
        return self.courses.zhidao

    def getZhidaoContext(self, RAC_id:str, force:bool=False):
        """
        ### fetch context for zhidao course
        * `RAC_id`: `recruitAndCourseId`
        * `force`: force update
        """
        if RAC_id in self.context and not force:
            return self.context[RAC_id]
        self._checkCookies()
        logger.info(f"Getting context for {RAC_id}")

        self._sessionReady()        # set cookies, headers, proxies
        self.session.headers.update({
            "Origin": "https://studyh5.zhihuishu.com",
            "Referer": "https://studyh5.zhihuishu.com/"
        })
        # cross sites login
        self.gologin(RAC_id)

        # get course info, including recruitId, course name, etc
        course = self.queryCourse(RAC_id)
        recruit_id = course.recruitId

        # get chapters
        chapters = self.videoList(RAC_id)
        course_id = chapters.courseId
        lesson_ids = []
        videos = ObjDict()
        for chapter in chapters.videoChapterDtos:
            for l in chapter.videoLessons:
                lesson_ids.append(l.id)
                if "videoId" in l: # this lesson has only one video
                    v = l.copy()
                    v.lessonId = l.id
                    v.id = 0
                    l.videoSmallLessons = [v]
                for v in l.videoSmallLessons: 
                    v.chapterId = chapter.id
                    videos[v.videoId] = v
        logger.info(f"{len(lesson_ids)} lessons, {len(videos)} videos")

        # get read-before, maybe unneccessary. BUTT hey, it's a POST request
        # self.queryStudyReadBefore(course_id, recruit_id)

        # get study info, including watchState, studyTotalTime
        video_ids = [video.id for video in videos.values() if video.id]
        states = self.queryStudyInfo(lesson_ids, video_ids, recruit_id)
        states.default = ObjDict(default=False)   # set default value for non exist attribute
        for v in videos.values():
            state = states.lv[str(v.id)] or states.lesson[str(v.lessonId)]
            v.watchState, v.studyTotalTime = state.watchState, state.studyTotalTime

        # get most recently viewed video id, probably unneccessary, again, it's a POST request
        self.queryUserRecruitIdLastVideoId(recruit_id)

        # update context
        ctx = ObjDict({
            "course": course,
            "chapters": chapters,
            "videos": videos,
            "cookies": self.session.cookies.copy(),
            "headers": self.session.headers.copy(),
            "fucked_time": 0
        }, default={})
        self.context[RAC_id] = ctx
        return ctx
        
    def fuckZhidaoCourse(self, RAC_id:str):
        """
        * `RAC_id`: `recruitAndCourseId`
        """
        logger.info(f"Fucking Zhidao course {RAC_id}")
        tprint = print if self.tree_view else lambda *a, **k: None

        # load context
        ctx = self.getZhidaoContext(RAC_id)
        course = ctx.course
        chapters = ctx.chapters
        
        # start fucking
        tprint(f"Fucking Zhidao course: {course.courseInfo.name or course.courseInfo.enName}")
        begin_time = time.time() # real world time
        prefix = self.prefix # prefix for tree-like print
        try:
            # 在 nohup 下运行无法获取，进行捕获
            w_lim = os.get_terminal_size().columns-1 # width limit for terminal output
        except Exception as e:
            # 考虑直接移除此变量，但是保留原代码风格，故进行赋值
            w_lim = 80
        try:
            for chapter in chapters.videoChapterDtos:
                tprint(prefix) # extra line as separator
                tprint(f"{prefix}__Fucking chapter {chapter.name}"[:w_lim])
                for lesson in chapter.videoLessons:
                    tprint(prefix*2)
                    tprint(f"{prefix*2}__Fucking lesson {lesson.name}"[:w_lim])
                    for video in lesson.videoSmallLessons:
                        tprint(f"{prefix*3}__Fucking video {video.name}"[:w_lim])
                        try:
                            self.fuckZhidaoVideo(RAC_id, video.videoId)
                        except TimeLimitExceeded as e:
                            logger.info(f"Fucking time limit exceeded: {e}")
                            self._pushplus("fuckZHS","刷课已完成")
                            self._bark("fuckZHS","刷课已完成")
                            tprint(prefix)
                            tprint(f"{prefix}##Fucking time limit exceeded: {e}\n")
                            return
                        except CaptchaException:
                            logger.info("Captcha required")
                            self._pushplus("fuckZHS","需要提供验证码")
                            self._bark("fuckZHS","需要提供验证码")
                            tprint(prefix)
                            tprint(f"{prefix}##Captcha required\a\n")
                            return
                        except Exception as e:
                            logger.exception(e)
                            self._pushplus("fuckZHS",e)
                            self._bark("fuckZHS",e)
                            tprint(f"{prefix*3}##Failed: {e}"[:w_lim])
        except KeyboardInterrupt:
            logger.info("User interrupted")
        wipeLine()
        tprint(prefix)
        tprint(f"\r{prefix}__Fucked course {course.courseInfo.name}, cost {time.time()-begin_time:.2f}s\n")
    
    def fuckZhidaoVideo(self, RAC_id, video_id):
        """
        * `RAC_id`: `recruitAndCourseId`
        * `video_id`: `videoId`
        """
        self._checkCookies()
        self._checkTimeLimit(RAC_id)
        ctx = self.getZhidaoContext(RAC_id)
        self._sessionReady(ctx)
        video = ctx.videos[video_id]
        played_time = video.studyTotalTime
        watch_state = video.watchState
        if not video:
            raise ValueError(f"Video {video_id} not found")
        if watch_state == 1 and self.end_thre <= 1.0:  # check end_thre in case someone wants to rewatch
            logger.info(f"Video {video.name} already watched")
            return
        # get token id from pre learning note
        token_id = self.prelearningNote(RAC_id, video_id).studiedLessonDto.id
        token_id = b64encode(str(token_id).encode()).decode()

        # get questions
        questions: ObjDict = self.loadVideoPointerInfo(RAC_id, video_id)
        questions.default = None
        questions = questions.questionPoint or []
        questions = sorted(questions, key=lambda x: x.timeSec, reverse=True) if questions else None
        while questions and questions[-1].timeSec <= played_time:
            questions.pop() # remove questions that are already answered

        # compute end time and make sure to answer all questions
        end_time = max(video.videoSec * self.end_thre, 1.0)
        if questions:
            end_time = max(questions[0].timeSec, end_time) # compare last question time with end_time

        # emulating video playing
        self.watchVideo(video.videoId)

        # no idea what it is
        self.threeDimensionalCourseWare(video.videoId)

        # prepare vars
        speed = self.speed or 1.5  # default speed for Zhidao is 1.5
        last_submit = played_time  # last pause time
        elapsed_time = 0    # real world time elapsed
        db_interval = 30    # database report interval
        cache_interval = 18 # cache report interval
        answer = None       # answer flag, do not modify
        report = False      # report flag, do not modify
        pause = 0           # pause flag, do not modify
        wp = WatchPoint()   # watch point, do not modify

        ##### start main event loop, sort of...
        while played_time < end_time:
            time.sleep(1)
            ctx.fucked_time += 1 # for time limit check
            elapsed_time += 1
            played_time = min(played_time+speed, end_time) # update video time and make sure not exceeding end_time
            pause = pause or int(random() < 0.0025)*60 # randomly pause a minute, may avoid detection
            report = report or pause == 60  # report on pause

            ### events
            ## on pause
            if pause:
                pause -= 1
                played_time = last_submit
            ## update watch point
            if not elapsed_time % 2:
                wp.add(played_time)
            ## get questions
            if questions and played_time >= questions[-1].timeSec:
                question = questions.pop()
                try:
                    question = self.lessonPopoupExam(RAC_id,
                                                    video_id,
                                                    question.questionIds
                                ).lessonTestQuestionUseInterfaceDtos[0].testQuestion
                    answer = 2    # answer delay time
                    report = True # set report flag
                except Exception as e:
                    logger.error(f"can't get question detail:\n{e}")
            ## answer questions
            if answer is not None:
                if answer == 0:
                    answer = None # unset answer flag
                    self.saveLessonPopupExamSaveAnswer(RAC_id, video_id, question.questionId, self.answerZhidao(question))
                else:
                    pause = pause or 1 # emulate pause on pop quiz
                    answer -= 1
            ## report to database
            if elapsed_time % db_interval == 0 or played_time >= end_time or report:
                report = False # unset report flag
                wp.add(played_time)
                # now submit to database
                self.saveDatabaseIntervalTimeV2(RAC_id,video_id,played_time,last_submit,wp.get(),token_id)
                last_submit = played_time # update last pause time
                wp.reset(played_time)     # reset watch point
            ## report to cache
            if False and elapsed_time % cache_interval == 0:
                wp.add(played_time)
                self.saveCacheIntervalTime(RAC_id,video_id,played_time,last_submit,wp.get(),token_id)
                last_submit = played_time # update last pause time
                wp.reset(played_time)     # reset watch point
            ### end events
            # print progress bar
            s, e = [60-pause, 60] if pause else [played_time, end_time]
            # have a glance of when quiz is answered
            action = "pause a minute" if pause else \
                    f"fucking {video.videoId}" if answer is None else "answering quiz"
            progressBar(s, e, prefix=action, suffix="done", progressbar_view=self.progressbar_view)
        ##### end main event loop
        time.sleep(random()+1) # old Joe needs more sleep

    def answerZhidao(self, q:dict):
        """you can override this function to answer questions"""
        q = ObjDict(q)
        a = [str(opt.id) for opt in q.questionOptions if opt.result=='1'] # choose correct answers
        return ','.join(a)

    def zhidaoQuery(self, url: str, data: dict, encrypt: bool = True, ok_code: int = 0,
                    setTimeStamp: bool = True, method: str = "POST", key=VIDEO_KEY, contentType: str = "form"):
        """set ok_code to None for no check"""
        cipher = Cipher(key)
        if setTimeStamp:
            # somehow their timestamps are ending with 000
            _t = int(time.time())*1000
            data["dateFormate"] = _t
        logger.debug(
            f"{method} url: {url}\nraw_data: {json.dumps(data,indent=4,ensure_ascii=False)}")
        form = {"secretStr": cipher.encrypt(
            json.dumps(data))} if encrypt else data

        if setTimeStamp:
            form["dateFormate"] = _t

        # 如果是POST请求，且contentType为json，将data转为json字符串
        if method == "POST" and contentType == "json":
            form = json.dumps(form)
        ret = self._apiQuery(url, data=form, method=method,
                             contentType=contentType)
        if ok_code is not None and ret.code != ok_code:
            ret.default = None
            match ret.code:
                case -12:
                    e = CaptchaException("captcha required")
                case _:
                    e = Exception(f"code: {ret.code} " +
                                  f"msg: {ret.message or json.dumps(ret,indent=4,ensure_ascii=False)}")
            logger.error(e)
            raise e
        return ret

    def gologin(self, RAC_id):
        '''### cross sites login for zhidao course'''
        login_url = "https://studyservice-api.zhihuishu.com/login/gologin"
        params = {"fromurl": f"https://studyh5.zhihuishu.com/videoStudy.html#/studyVideo?recruitAndCourseId={RAC_id}"}
        logger.debug(f"GET {login_url}\nparams: {params}\n")
        return self.session.get(login_url, params=params, proxies=self.proxies, timeout=10)

    def queryCourse(self, RAC_id):
        '''### query course info for zhidao share course'''
        course_url = "https://studyservice-api.zhihuishu.com/gateway/t/v1/learning/queryCourse"
        return self.zhidaoQuery(course_url, {"recruitAndCourseId": RAC_id}).data

    def videoList(self, RAC_id):
        '''### query video/chapter list for zhidao share course'''
        videos_url = "https://studyservice-api.zhihuishu.com/gateway/t/v1/learning/videolist"
        chapters = self.zhidaoQuery(videos_url, {"recruitAndCourseId": RAC_id}).data
        chapters.default = [] # set default value for non exist attribute
        return chapters

    def queryStudyReadBefore(self, course_id, recruit_id):
        '''### query study read before for zhidao share course'''
        read_url = "https://studyservice-api.zhihuishu.com/gateway/t/v1/learning/queryStudyReadBefore"
        return self.zhidaoQuery(read_url, data={"courseId": course_id, "recruitId": recruit_id}, ok_code=None).data

    def queryStudyInfo(self, lesson_ids:list, video_ids:list, recruit_id):
        '''### query study info for zhidao'''
        state_url = "https://studyservice-api.zhihuishu.com/gateway/t/v1/learning/queryStuyInfo" # NOT MY TYPO
        data = {
            "lessonIds": lesson_ids,
            "lessonVideoIds": video_ids,
            "recruitId": recruit_id
        }
        return self.zhidaoQuery(state_url, data=data).data

    def queryUserRecruitIdLastVideoId(self, recruit_id):
        '''### query user recruit id last video id for zhidao'''
        last_url   = "https://studyservice-api.zhihuishu.com/gateway/t/v1/learning/queryUserRecruitIdLastVideoId"
        return self.zhidaoQuery(last_url, data={"recruitId": recruit_id}).data

    def prelearningNote(self, RAC_id, video_id):
        '''### query prelearning note for zhidao'''
        note_url = "https://studyservice-api.zhihuishu.com/gateway/t/v1/learning/prelearningNote"

        ctx = self.getZhidaoContext(RAC_id)
        course_id = ctx.chapters.courseId
        recruit_id = ctx.course.recruitId
        video = ctx.videos[video_id]
        data = {
            "ccCourseId": course_id,
            "chapterId": video.chapterId,
            "isApply": 1,
            "lessonId": video.lessonId, # this.lessonId
            "lessonVideoId": video.id, # this.smallLessonId
            "recruitId": recruit_id,
            "videoId": video.videoId 
        }
        return self.zhidaoQuery(note_url, data=data).data

    def loadVideoPointerInfo(self, RAC_id, video_id):
        '''### query video pointer info for zhidao'''
        event_url = "https://studyservice-api.zhihuishu.com/gateway/t/v1/popupAnswer/loadVideoPointerInfo"
        ctx = self.getZhidaoContext(RAC_id)
        course_id = ctx.chapters.courseId
        recruit_id = ctx.course.recruitId
        video = ctx.videos[video_id]
        data = {
            "lessonId": video.lessonId,
            "lessonVideoId": video.id, 
            "recruitId": recruit_id, 
            "courseId": course_id
        }
        return self.zhidaoQuery(event_url, data=data).data

    def lessonPopoupExam(self, RAC_id, video_id, question_ids:list):
        '''### query lesson popoup exam for zhidao'''
        getQ_url = "https://studyservice-api.zhihuishu.com/gateway/t/v1/popupAnswer/lessonPopupExam"
        ctx = self.getZhidaoContext(RAC_id)
        video = ctx.videos[video_id]
        data={
            "lessonId": video.lessonId, # this.lessonId
            "lessonVideoId": video.id, # this.smallLessonId
            "questionIds" : question_ids
        }
        return self.zhidaoQuery(getQ_url, data).data

    def saveLessonPopupExamSaveAnswer(self, RAC_id, video_id, question_id, answer_ids:str):
        '''### save lesson popup exam save answer for zhidao'''
        subQ_url = "https://studyservice-api.zhihuishu.com/gateway/t/v1/popupAnswer/saveLessonPopupExamSaveAnswer"
        ctx = self.getZhidaoContext(RAC_id)
        course_id = ctx.chapters.courseId
        recruit_id = ctx.course.recruitId
        video = ctx.videos[video_id]
        data={
            "courseId": course_id, # this.courseId,
            "recruitId": recruit_id, # this.recruitId
            "testQuestionId": question_id, # this.pageList.testQuestion.questionId
            "isCurrent": '1', # this.result ...it should be 'isCorrect'... in the name of lord, can somebody teach them eNgLIsH!!
            "lessonId": video.lessonId, # this.lessonId
            "lessonVideoId": video.id, # this.smallLessonId
            "answer": answer_ids, # this.answerStu.join(",")
            "testType": 0 # always 0
        }
        return self.zhidaoQuery(subQ_url, data).data

    def saveDatabaseIntervalTime(self, RAC_id, video_id, played_time, last_submit, watch_point, token_id=None):
        '''### save database interval time for zhidao'''
        record_url = "https://studyservice-api.zhihuishu.com/gateway/t/v1/learning/saveDatabaseIntervalTime"
        ctx = self.getZhidaoContext(RAC_id)
        recruit_id = ctx.course.recruitId
        video = ctx.videos[video_id]
        raw_ev = [
            recruit_id,
            video.lessonId, # this.lessonId
            video.id, # this.smallLessonId
            video.videoId, # this.videoId
            video.chapterId, # this.chapterId
            '0', # this.data.studyStatus, always 0
            int(played_time-last_submit), # this.playTimes
            int(played_time), # this.totalStudyTime
            HMS(seconds=min(video.videoSec, # more realistic
                            int(played_time+randint(29,31)))) 
        ]
        if not token_id:
            token_id = self.prelearningNote(RAC_id, video_id).studiedLessonDto.id
            token_id = b64encode(str(token_id).encode()).decode()
        data = {
            "watchPoint": watch_point,
            "ev": getEv(raw_ev),
            "learningTokenId": token_id
        }
        return self.zhidaoQuery(record_url, data=data).data

    def threeDimensionalCourseWare(self, video_id):
        '''### query three dimensional course ware for zhidao'''
        ware_url = "https://studyservice-api.zhihuishu.com/gateway/t/v1/course/threeDimensionalCourseWare"
        params = {"videoId": video_id}
        return self.zhidaoQuery(ware_url, data=params, method="GET").data

    def saveDatabaseIntervalTimeV2(self, RAC_id, video_id, played_time, last_submit, watch_point, token_id=None, initial=False):
        '''### save database interval time for zhidao'''
        record_url = "https://studyservice-api.zhihuishu.com/gateway/t/v1/learning/saveDatabaseIntervalTimeV2"
        ctx = self.getZhidaoContext(RAC_id)
        recruit_id = ctx.course.recruitId
        video = ctx.videos[video_id]
        if initial: # sometimes a request like this happens, I originally thought it is the initialization request, but I might be wrong
            raw_ev = [
                recruit_id,
                video.chapterId, # this.chapterId
                ctx.course.courseInfo.courseId,
                video.lessonId, # this.smallLessonId
                HMS(seconds=min(video.videoSec, int(played_time))) ,
                int(played_time),
                video.videoId, # this.videoId
                '0', # this.data.studyStatus, always 0
                int(played_time), # this.totalStudyTime
                self.uuid
            ]
        else:
            raw_ev = [
                recruit_id,
                video.lessonId, # this.lessonId
                video.id, # this.smallLessonId
                video.videoId, # this.videoId
                video.chapterId, # this.chapterId
                '0', # this.data.studyStatus, always 0
                int(played_time-last_submit), # this.playTimes
                int(played_time), # this.totalStudyTime
                HMS(seconds=min(video.videoSec, int(played_time))),
                self.uuid + "zhs"
            ]
        if not token_id:
            token_id = self.prelearningNote(RAC_id, video_id).studiedLessonDto.id
            token_id = b64encode(str(token_id).encode()).decode()
        data = {
            "ewssw": watch_point,
            "sdsew": getEv(raw_ev),
            "zwsds": token_id,
            "courseId": ctx.course.courseInfo.courseId
        }
        if initial:
            data.pop("courseId")
        return self.zhidaoQuery(record_url, data=data).data

    def saveCacheIntervalTime(self, RAC_id, video_id, played_time, last_submit, watch_point, token_id=None):
        '''### save cache interval time for zhidao'''
        cache_url  = "https://studyservice-api.zhihuishu.com/gateway/t/v1/learning/saveCacheIntervalTime"
        ctx = self.getZhidaoContext(RAC_id)
        recruit_id = ctx.course.recruitId
        course_id = ctx.chapters.courseId
        video = ctx.videos[video_id]
        #!! NOTICE: content is different from database
        raw_ev = [
            recruit_id,
            video.chapterId,
            course_id,
            video.lessonId,
            HMS(seconds=min(video.videoSec, # more realistic
                            int(played_time+randint(10,20)))),
            int(played_time),
            video.videoId,
            video.id,
            int(played_time-last_submit),
        ]
        if not token_id:
            token_id = self.prelearningNote(RAC_id, video_id).studiedLessonDto.id
            token_id = b64encode(str(token_id).encode()).decode()
        data = {
            "watchPoint": watch_point,
            "ev": getEv(raw_ev),
            "learningTokenId": token_id
        }
        return self.zhidaoQuery(cache_url, data=data).data

# end of zhidao methods
#############################################
# following are methods for hike API
    def getHikeList(self):
        """
        ### Get all courses of zhidao from server
        """
        if self.courses.hike:
            return self.courses.hike
        url = "https://hikeservice.zhihuishu.com/student/course/aided/getMyCourseList"
        self._checkCookies()
        self._sessionReady()
        params = {
            "uuid": self.uuid,
            "data": datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%S.%f")[:-3] + "Z"
        }
        r = self._apiQuery(url, params, "GET").result
        r.default = None
        self.courses.hike = r.startInngcourseList or []# I've given up on their eNgLIsH
        return self.courses.hike

    def getHikeContext(self, course_id:str, force:bool=False):
        if course_id in self.context and not force:
            return self.context[course_id]
        self._checkCookies()
        self._sessionReady() # set cookies, headers, proxies
        self.session.headers.update({
            "Origin": "https://hike.zhihuishu.com",
            "Referer": "https://hike.zhihuishu.com/"
        })
        root = self.queryResourceMenuTree(course_id)
        ctx = ObjDict({
            "root": root,
            "cookies": self.session.cookies.copy(),
            "headers": self.session.headers.copy(),
            "fucked_time": 0
        }, default={})
        self.context[course_id] = ctx
        return ctx
    
    def fuckHikeCourse(self, course_id:str):
        tprint = print if self.tree_view else lambda *a, **k: None
        begin_time = time.time()
        root = self.getHikeContext(course_id).root
        
        prefix = self.prefix
        logger.info(f"Fucking Hike course {course_id} (total root chapters: {len(root)})")
        tprint(f"Fucking course {course_id} (total root chapters: {len(root)})")
        try:
            for chapter in root:
                self._traverse(course_id, chapter)
        except KeyboardInterrupt:
            logger.info("user interrupted")
        logger.info(f"Fucked course {course_id}, cost {time.time()-begin_time}s")
        wipeLine()
        tprint(prefix)
        tprint(f"{prefix}__Fucked course {course_id}, cost {time.time()-begin_time:.2f}s\n")

    def fuckHikeVideo(self, course_id, file_id, prev_time=0):
        self._checkCookies()
        self._checkTimeLimit(course_id)
        logger.info(f"Fucking Hike video {file_id} of course {course_id}")
        begin_time = time.time()
        ctx = self.getHikeContext(course_id)
        self._sessionReady(ctx) # set cookies, headers, proxies
        # get video info
        file_info = self.stuViewFile(course_id, file_id)

        # emulating video playing
        self.watchVideo(file_info.dataId)

        # getting ready to fuck
        total_time = int(file_info.totalTime)
        start_date = int(time.time()*1000)
        speed = self.speed or 1.25 # default speed for Hike is 1.25
        interval = 30              # interval between 2 progess reports
        end_time = max(total_time*self.end_thre, 1.0)
        played_time = prev_time    # total video played time
        # start main loop
        while played_time <= end_time:
            time.sleep(1)
            ctx.fucked_time += 1
            played_time = min(played_time+speed, end_time)
            # enter branch when video is finished or interval is reached
            if played_time >= end_time or \
                not (int(played_time-prev_time) % interval):
                ret_time = self.saveStuStudyRecord(course_id,file_id,played_time,prev_time,start_date) # report progress
                prev_time, played_time = ret_time, ret_time
            progressBar(played_time, end_time, prefix=f"fucking {file_id}", suffix="done", progressbar_view=self.progressbar_view)
        logger.info(f"Fucked video {file_id} of course {course_id}, cost {time.time()-begin_time:.2f}s")
        time.sleep(random()+1) # more human-like

    def fuckFile(self, course_id, file_id):
        self.stuViewFile(course_id, file_id)
        time.sleep(random()*2+1) # more human-like

    def _traverse(self,course_id, node: ObjDict, depth=0):
        depth += 1
        tprint = print if self.tree_view else lambda *a, **k: None
        try:
            # 在 nohup 下运行无法获取，进行捕获
            w_lim = os.get_terminal_size().columns-1 # width limit for terminal output
        except Exception as e:
            # 考虑直接移除此变量，但是保留原代码风格，故进行赋值
            w_lim = 80
        prefix = self.prefix * depth
        if node.childList: # if childList is not None, then it's a chapter
            chapter = node
            logger.debug(f"Fucking chapter {chapter.id}")
            tprint(prefix) # separate chapters
            tprint(f"{prefix}__Fucking chapter {chapter.name}"[:w_lim])
            for child in chapter.childList:
                self._traverse(course_id, child, depth=depth)
        else: # if childList is None, then it's a file
            file = node
            file.studyTime = file.studyTime or 0 # sometimes it's None
            logger.debug(f"Fucking file {file.id}, data type: {file.dataType}")
            tprint(f"{prefix}__Fucking {file.name}"[:w_lim])

            if file.studyTime >= file.totalTime*self.end_thre:
                logger.debug(f"Skipped file {file.id}")
                return

            try:
                match file.dataType:
                    case 3:
                        self.fuckHikeVideo(course_id, file.id, file.studyTime)
                    case None:
                        tprint(f"{prefix}##Unsupported file type, may be a quiz"[:w_lim])
                    case _:
                        self.fuckFile(course_id, file.id)
            except TimeLimitExceeded as e:
                logger.info(f"Time limit exceeded, video {file.id} skipped")
                tprint(f"{prefix}##Time limit exceeded: {e}")
            except Exception as e:
                logger.error(f"Failed to fuck file {file.id} of course {course_id}")
                logger.exception(e)
                tprint(f"{prefix}##Failed: {e}"[:w_lim])

    def hikeQuery(self, url:str, data:dict,sig:bool=False, ok_code:int=200,
                   setTimeStamp:bool=True, method:str="GET"):
        """set ok_code to None for no check"""
        if setTimeStamp:
            data["_"] = int(time.time()*1000) # miliseconds
        if sig:
            for k,v in data.items():
                data[k] = str(v)
            data["signature"] = sign(data)
        ret = self._apiQuery(url, data, method=method)
        if ok_code is not None and int(ret.status) != ok_code:
            ret.default = None
            e = Exception(f"{ret.status} {ret.message or json.dumps(ret,indent=4,ensure_ascii=False)}")
            logger.error(e)
            raise e
        return ret

    def queryResourceMenuTree(self, course_id):
        '''### get resource menu tree for hike'''
        url = "https://studyresources.zhihuishu.com/studyResources/stuResouce/queryResourceMenuTree"
        params = {"courseId": course_id}
        return self.hikeQuery(url, params).rt

    def stuViewFile(self, course_id, file_id):
        '''### get resource menu tree for hike'''
        parse_url = "https://studyresources.zhihuishu.com/studyResources/stuResouce/stuViewFile"
        params = {
            "courseId": course_id,
            "fileId": file_id
        }
        # get video info
        return self.hikeQuery(parse_url, params).rt

    def saveStuStudyRecord(self, course_id, file_id, played_time, prev_time, start_date):
        '''### save study record for hike'''
        url = "https://hike-teaching.zhihuishu.com/stuStudy/saveStuStudyRecord"
        params = {
            "uuid": self.uuid,
            "courseId": course_id,
            "fileId": file_id,
            "studyTotalTime": int(played_time-prev_time),
            "startWatchTime": int(prev_time),
            "endWatchTime": int(played_time),
            "startDate": start_date,
            "endDate": int(time.time()*1000),
        }
        rt = self.hikeQuery(url, params, sig=True, ok_code=200).rt
        if rt is None:
            raise Exception("Failed to save study record")
        return rt

# end of hike methods
#######################################
# shared methods
    def watchVideo(self, video_id): # it's probably unnecessary but let's keep it to fool those idiots
        headers = self.session.headers.copy()
        cookies = self.session.cookies.copy()
        parse_url = "https://newbase.zhihuishu.com/video/initVideo"
        def watch():
            # get video link
            r = requests.get(parse_url, params={
                                "jsonpCallBack": "result",
                                "videoID": str(video_id),
                                "_": int(time.time()*1000)
                            },
                            cookies=cookies, headers=headers, proxies=self.proxies, timeout=10)
            r = re.match(r"^result\((.*)\)$",r.text).group(1)
            url = ObjDict(json.loads(r)).result.lines[0].lineUrl
            try:
                requests.get(url, headers=headers, cookies=cookies, proxies=self.proxies)
            except Exception as e:
                logger.error(f"Failed to watch video {video_id}")
                logger.exception(e)
        watch_thread = Thread(target=watch)
        watch_thread.start()

    def _apiQuery(self, url: str, data: dict, method: str = "POST", contentType: str = "form"):
        method = method.upper()
        logger.debug(f"{method} url: {url}\ndata: {json.dumps(data,indent=4,ensure_ascii=False)}\n" +
                     f"headers: {json.dumps(self.headers, indent=4)}\n" +
                     f"cookies: {self.session.cookies}\n" +
                     f"proxies: {json.dumps(self.session.proxies, indent=4)}")
        match method:
            case "POST":
                # set content-type
                if contentType == "json":
                    self.session.headers.update({
                        "Content-Type": "application/json;charset=UTF-8"
                    })
                    if type(data) == dict:
                        data = json.dumps(data)
                r = self.session.post(
                    url, data=data, proxies=self.proxies, timeout=10)

                # set content-type back
                self.session.headers.pop("Content-Type", None)

            case "GET":
                r = self.session.get(
                    url, params=data, proxies=self.proxies, timeout=10)
            case _:
                e = ValueError(f"Unsupport method: {method}")
                logger.error(e)
                raise e
        ret = ObjDict(r.json())
        logger.debug(json.dumps(ret, indent=4, ensure_ascii=False))
        return ret

    def _checkCookies(self):
        if not self._cookies:
            e = Exception("No cookies found, please login first")
            logger.error(e)
            raise e

    def _checkTimeLimit(self, cid):
        if self.limit and self.context[cid].fucked_time >= self.limit*60:
            raise TimeLimitExceeded(f"{self.limit} minutes")

    def _sessionReady(self, ctx:dict=None):
        ctx = ObjDict(ctx or {}, recursive=False, default=False)
        self.session.cookies = ctx.cookies or self.cookies.copy()
        self.session.headers = ctx.headers or self.headers.copy()
        self.session.proxies = self.proxies.copy()

    def zhidaoAiExamQuery(self, url: str, data: dict, encrypt: bool = True, ok_code: int = 0,
                          setTimeStamp: bool = True, method: str = "POST", key=VIDEO_KEY, contentType: str = "form"):
        """set ok_code to None for no check"""

        self._checkCookies()
        self._sessionReady()
        return self.zhidaoQuery(url, data, encrypt, ok_code, setTimeStamp, method, key, contentType)

    def getZhidaoAiList(self):
        """
        ### 取得智慧树AI课程列表
        """
        url = "https://onlineservice-api.zhihuishu.com/gateway/t/v1/student/queryStudentAICourseList"
        self._checkCookies()
        self._sessionReady()
        data = {"status": 3}
        ret = self.zhidaoQuery(url, data, ok_code=None, key=HOME_KEY).rt

        return ret

    def getAiKnowlegePoints(self, course_id: int, class_id: int):
        """
        ### 取得智慧树AI课程的知识点
        * `course_id`: 课程ID
        * `class_id`: 班级ID
        """
        url = "https://kg-ai-run.zhihuishu.com/run/gateway/t/stu/knowledge-study/course-basic"
        self._checkCookies()
        self._sessionReady()
        data = {"courseId": course_id, "classId": class_id}
        ret = self.zhidaoQuery(url, data, ok_code=200,
                               key=AI_KEY, contentType="json").data

        return ret

    def aiResourseComplete(self, courseId: int, classId: int, knowledgeId: int, resourcesUid: int, watchUId: int):
        """
        ### 完成智慧树AI课程的资源
        """
        url = "https://kg-ai-run.zhihuishu.com/run/gateway/t/stu/studyRecord/completed"
        self._checkCookies()
        self._sessionReady()
        data = {"courseId": courseId, "classId": classId, "knowledgeId": knowledgeId,
                "resourcesUid": resourcesUid, "watchUId": watchUId}
        ret = self.zhidaoQuery(url, data, ok_code=200,
                               key=AI_KEY, contentType="json").data

        return ret

    def reportAiVideoProcess(self, courseId: int, classId: int, fileId: int, knowledgeId: int, lastWatchTime: int, studyTotalTime: int = 10, shareCourseId: str = "", nodeType: int = 0, watchUId: int = 1):
        """
        ### 上传智慧树AI视频观看进度
        """
        url = "https://kg-ai-run.zhihuishu.com/run/gateway/t/stu/studyRecord/report"
        self._checkCookies()
        self._sessionReady()

        now = int(time.time() * 1000)
        data = {"courseId": courseId, "classId": classId, "fileId": fileId, "knowledgeId": knowledgeId, "lastWatchTime": lastWatchTime,
                "studyTotalTime": studyTotalTime, "shareCourseId": shareCourseId, "nodeType": nodeType, "watchUId": watchUId, "dateFormate": now}
        try:
            ret = self.zhidaoQuery(
                url, data, ok_code=200, key=AI_KEY, contentType="json").data
            return True
        except Exception as e:
            logger.exception(e)
            return False

    def listKnowledgeResources(self, courseId: int, classId: int, knowledgeId: int):
        """
        ### 取得智慧树AI课程的知识点资源列表
        """
        url = "https://kg-ai-run.zhihuishu.com/run/gateway/t/stu/resources/list-knowledge-resource"
        self._checkCookies()
        self._sessionReady()
        data = {"courseId": courseId, "classId": classId,
                "knowledgeId": knowledgeId}
        ret = self.zhidaoQuery(url, data, ok_code=200,
                               key=AI_KEY, contentType="json").data

        return ret

    def queryAiExam(self, courseId: int, classId: int, knowledgeId: int) -> dict:
        """
        ### 取得智慧树AI课程的考试信息
        """
        url = "https://kg-ai-run.zhihuishu.com/run/gateway/t/stu/exam/questions-paper"
        self._checkCookies()
        self._sessionReady()
        data = {
            "scMapId": courseId,
            "courseId": classId,
            "classId": classId,
            "knowledgeId": knowledgeId,
        }

        try:
            ret = self.zhidaoQuery(
                url, data, ok_code=200, key=AI_KEY, contentType="json").data
            return ret

        except Exception as e:
            logger.exception(e)
            return None

    def fuckAiVideo(self, courseId: int, classId: int, fileId: int, knowledgeId: int, watchUId: int = 1, startAt: int = 0):
        """
        ### 观看智慧树AI视频
        """
        # 取得视频长度
        url = "https://kg-ai-run.zhihuishu.com/run/gateway/t/stu/resources-lab/get-video-time"
        self._checkCookies()
        self._sessionReady()
        data = {"courseId": courseId,
                "classId": classId, "videoIdList": [fileId]}

        try:
            ret = self.zhidaoQuery(
                url, data, ok_code=200, key=AI_KEY, contentType="json").data
            video_length = ret[0].time
        except Exception as e:
            logger.exception(e)
            raise Exception("Failed to get video length")

        self.watchVideo(fileId)

        played_time = startAt
        # 开始观看
        while played_time < video_length:
            # 上传视频观看进度
            played_time = min(
                int(round(played_time + (self.speed or 1.5) * 2)), video_length)
            try:
                self.reportAiVideoProcess(
                    courseId, classId, fileId, knowledgeId, played_time, watchUId=watchUId)
            except Exception as e:
                logger.exception(e)

            time.sleep(2)

            if self.progressbar_view:
                # print progress bar
                s, e = [played_time, video_length]
                action = f"fucking {fileId}"
                progressBar(s, e, prefix=action,
                            suffix=f"({played_time}/{video_length})")

    def fuckAiCourse(self, courseId: int, classId: int, aiConfig: dict, no_exam: bool = False):
        """
        ### 观看智慧树AI课程
        """
        tree_view = self.tree_view

        logger.info(f"Fucking AI course {courseId} in class {classId}")
        tprint = print if tree_view else lambda *a, **k: None

        # 取得课程信息
        try:
            knowledgePoints = self.getAiKnowlegePoints(courseId, classId)

            tprint(f"Fucking Zhidao AI course: {knowledgePoints.courseName}")

            begin_time = time.time()  # real world time
            prefix = self.prefix  # prefix for tree-like print
            w_lim = os.get_terminal_size().columns-1  # width limit for terminal output

            cakeThemeList = knowledgePoints.cakeThemeList
        except Exception as e:
            logger.exception(e)
            raise Exception("Failed to get knowledge points")

        # 遍历主题
        for theme in cakeThemeList:
            tprint(prefix)  # extra line as separator
            tprint(f"{prefix}__Fucking theme {theme.themeName}"[:w_lim])
            # 取得知识点列表
            try:
                knowledgeList = theme.knowledgeList
            except Exception as e:
                logger.exception(e)
                tprint(prefix*2)
                tprint(
                    f"{prefix*2}__Theme {theme.themeName} has no knowledge points")
                continue

            # 遍历知识点
            for knowledge in knowledgeList:
                ppts = []
                ppt_conf = aiConfig.get("ppt_processing", {})
                moonShot_conf = ppt_conf.get("moonShot", {})
                tprint(prefix*2)  # extra line as separator
                tprint(
                    f"{prefix*2}__Fucking knowledge point {knowledge.knowledgeName}"[:w_lim])

                    # 获取资源列表
                if knowledge.studyProgress < 100:  # knowledge point not fucked
                    try:
                        resources = self.listKnowledgeResources(
                            courseId, classId, knowledge.knowledgeId)
                        resourceList = resources.resourceList
                    except Exception as e:
                        logger.exception(e)
                        tprint(prefix*3)
                        tprint(
                            f"{prefix*3}__Failed to get resources for knowledge point {knowledge.knowledgeName}")
                        continue
                    # 遍历资源
                    for resource in resourceList:
                        time.sleep(randint(1, 10) * 0.2)  # random delay
                        tprint(prefix*3)  # extra line as separator
                        tprint(
                            f"{prefix*3}__Fucking resource {resource.resourcesDetail.resourcesName}"[:w_lim])

                        # 判断资源类型
                        resourceType = resource.resourcesDetail.resourcesType
                        resourceDistributeType = resource.resourcesDetail.resourcesDistributeType
                        if resource.studyStatus == 1:  # already fucked
                            tprint(prefix*4)
                            tprint(f"{prefix*4}__Resource already fucked")

                            if resourceType == 1 and resourceDistributeType == 4:  # ppt
                                pptName = resource.resourcesDetail.resourcesName
                                pptUrl = resource.resourcesDetail.resourcesUrl

                                ppts.append({
                                    "name": pptName,
                                    "url": pptUrl
                                })
                            continue

                        # text or powerpoint
                        if (resourceType == 2 and resourceDistributeType == 1) or (resourceType == 1 and resourceDistributeType == 4):
                            try:
                                self.aiResourseComplete(
                                    courseId, classId, knowledge.knowledgeId, resource.resourcesDetail.resourcesUid, 1)
                                tprint(prefix*4)
                                tprint(
                                    f"{prefix*4}__Resource type is {'text' if resourceType == 2 else 'ppt'}, fucked")
                                
                                resourceType = resource.resourcesDetail.resourcesType
                                resourceDistributeType = resource.resourcesDetail.resourcesDistributeType

                                if resourceType == 1 and resourceDistributeType == 4:  # ppt
                                    pptName = resource.resourcesDetail.resourcesName
                                    pptUrl = resource.resourcesDetail.resourcesUrl

                                    ppts.append({
                                        "name": pptName,
                                        "url": pptUrl
                                    })
                            except Exception as e:
                                logger.exception(e)
                                tprint(prefix*4)
                                tprint(
                                    f"{prefix*4}__Failed to fuck text/ppt resource {resource.resourcesDetail.resourcesName}")
                        elif resourceType == 1 and resourceDistributeType == 3:  # video
                            try:
                                self.fuckAiVideo(
                                    courseId, classId, resource.resourcesDetail.resourcesFileId, knowledge.knowledgeId, 1)
                                tprint(prefix*4)
                                tprint(
                                    f"{prefix*4}__Fucked video {resource.resourcesDetail.resourcesName}")
                            except Exception as e:
                                logger.exception(e)
                                tprint(prefix*4)
                                tprint(
                                    f"{prefix*4}__Failed to fuck video {resource.resourcesDetail.resourcesName}, {e}")
                        elif resourceType == 2 and resourceDistributeType == 2:  # 新增的条件，处理智慧树课程视频
                            try:
                                # 假设我们使用与普通视频相同的方法来处理这种资源
                                self.fuckAiVideo(
                                    courseId, classId, resource.resourcesDetail.resourcesFileId, knowledge.knowledgeId, 1)
                                tprint(prefix*4)
                                tprint(
                                    f"{prefix*4}__Fucked Zhihuishu course video {resource.resourcesDetail.resourcesName}")
                            except Exception as e:
                                logger.exception(e)
                                tprint(prefix*4)
                                tprint(
                                    f"{prefix*4}__Failed to fuck Zhihuishu course video {resource.resourcesDetail.resourcesName}, {e}")
                        else:
                            tprint(prefix*4)
                            try:
                                self.aiResourseComplete(
                                    courseId, classId, knowledge.knowledgeId, resource.resourcesDetail.resourcesUid, 1)
                                tprint(
                                    f"{prefix*4}__Resource type is {resourceType}, distribute type is {resourceDistributeType}, fucked")
                            except Exception as e:
                                logger.exception(e)
                                tprint(
                                    f"{prefix*4}__Failed to fuck resource {resource.resourcesDetail.resourcesName}, {e}")
                            continue

                    tprint(prefix*3)  # extra line as separator
                    tprint(
                        f"{prefix*3}__Fucked knowledge point {knowledge.knowledgeName}")
                else:
                    if ppt_conf.get("provide_to_ai", False) and moonShot_conf.get("api_key", ""):
                        try:
                            resources = self.listKnowledgeResources(
                                courseId, classId, knowledge.knowledgeId)
                            resourceList = resources.resourceList
                        except Exception as e:
                            logger.exception(e)
                            tprint(prefix*3)
                            tprint(
                                f"{prefix*3}__Failed to get resources for knowledge point {knowledge.knowledgeName}")
                            continue
                        for resource in resourceList:
                            resourceType = resource.resourcesDetail.resourcesType
                            resourceDistributeType = resource.resourcesDetail.resourcesDistributeType
                            if resourceType == 1 and resourceDistributeType == 4:  # ppt
                                pptName = resource.resourcesDetail.resourcesName
                                pptUrl = resource.resourcesDetail.resourcesUrl

                                ppts.append({
                                    "name": pptName,
                                    "url": pptUrl
                                })
                    tprint(prefix*3)
                    tprint(f"{prefix*3}__Knowledge point already fucked")

                # 开始测试部分
                tried_count = 0
                while True:
                    if no_exam:
                        break

                    tprint(prefix*3)
                    tprint(
                        f"{prefix*3}__Starting exam for knowledge point {knowledge.knowledgeName}")
                    exam = self.queryAiExam(
                        courseId, classId, knowledge.knowledgeId)
                    if not exam or not exam.get("paperId"):
                        tprint(prefix*4)
                        tprint(
                            f"{prefix*4}__No exam available for this knowledge point")
                        break

                    mastery_score = exam.get("masteryScore", None)
                    if not mastery_score:
                        mastery_score = 0
                    if mastery_score < 30 and tried_count > 4:
                        tprint(prefix*4)
                        tprint(
                            f"{prefix*4}__Mastery score below 30, tried {tried_count} times, giving up")
                        break

                    tried_count += 1
                    if mastery_score is not None and mastery_score > 90:
                        tprint(prefix*4)
                        tprint(
                            f"{prefix*4}__Mastery score already above 90: {exam['masteryScore']}")
                        break

                    exam_ctx = ExamCtx(fucker=self,
                                       courseId=courseId,
                                       knowledgeId=knowledge.knowledgeId,
                                       examTestId=exam["examTestId"],
                                       examPaperId=exam["paperId"],
                                       opExtra={
                                           "courseName": knowledgePoints.courseName,
                                           "theme": theme.themeName,
                                           "knowledgePoint": knowledge.knowledgeName
                                       },
                                       progress_view=self.progressbar_view,
                                       aiConfig=aiConfig
                                       )

                    # 将ppt转为text
                    if ppt_conf.get("provide_to_ai", False) and moonShot_conf.get("api_key", ""):
                        ppt2txt = PptToTxt(moonShotKey=moonShot_conf.get("api_key", ""),baseUrl=moonShot_conf.get("base_url","https://api.moonshot.cn/v1"))
                        for ppt in ppts:
                            try:
                                content = ppt2txt.parseTxt(ppt["url"])
                                ppt["content"] = content
                                tprint(prefix*4)
                                tprint(
                                    f"{prefix*4}__Converted ppt {ppt['name']} to text")
                            except Exception as e:
                                logger.exception(e)
                                tprint(prefix*4)
                                tprint(
                                    f"{prefix*4}__Failed to convert ppt {ppt['name']}, {e}")

                    is_success, correct_count, total_count = exam_ctx.startFuck(referenceMaterials=ppts)

                    tprint(prefix*4)
                    tprint(
                        f"{prefix*4}__Exam attempt: Success: {is_success}, Score: {correct_count}/{total_count}")

                    # random sleep to avoid being detected as a bot
                    time.sleep(math.ceil(uniform(0.5, 1.5)))

                    tprint(prefix*3)
                    tprint(
                        f"{prefix*3}__Finished exam for knowledge point {knowledge.knowledgeName}")

            tprint(prefix*2)  # extra line as separator
            tprint(f"{prefix*2}__Fucked theme {theme.themeName}")

            # random sleep to avoid being detected as a bot
            time.sleep(math.ceil(uniform(0.5, 1.5)))

        tprint(prefix)  # extra line as separator
        tprint(
            f"{prefix}__Fucked Zhidao AI course {knowledgePoints.courseName} in {time.time()-begin_time:.2f}s")

#############################################
# following are methods for smart course (智慧课程) API
# host: kg-ai-run.zhihuishu.com/run/gateway/t/stu
# web page: ai-smart-course-student-pro.zhihuishu.com/singleCourse/knowledgeStudy/<courseId>/<classId>
# the API is the same gateway as AI course, use AI_KEY to encrypt the json body
#############################################
    def getSmartCourseList(self):
        """
        ### 取得智慧课程列表（学生视角）
        """
        if self.courses.smart:
            return self.courses.smart
        self._checkCookies()
        self._sessionReady()
        r = self.zhidaoQuery(
            SMART_BASE + "/center/course-list-home", {}, ok_code=200, key=AI_KEY, contentType="json")
        r.default = None
        self.courses.smart = r.data or []
        return self.courses.smart

    def getSmartCourseContext(self, courseId, classId, force: bool = False):
        """
        ### 取得智慧课程的上下文（知识点树/课程信息）
        * courseId: 课程 ID（网址中的第一个 ID）
        * classId: 班级 ID（网址中的第二个 ID）
        """
        key = f"smart_{courseId}_{classId}"
        if key in self.context and not force:
            return self.context[key]
        self._checkCookies()
        self._sessionReady()
        logger.info(f"Getting smart course context for {courseId}/{classId}")

        basic = self.smartQuery("/knowledge-study/course-basic",
                                {"courseId": courseId, "classId": classId}).data
        themes = self.smartQuery("/knowledge-study/list-knowledge-theme",
                                 {"courseId": courseId, "classId": classId}).data
        themes.default = []
        courseThemeList = themes.courseThemeList or []

        # flatten the theme tree into a simple knowledge list
        knowledge_list = []
        for theme in courseThemeList:
            for subTheme in theme.subThemeList or []:
                for knowledge in subTheme.knowledgeList or []:
                    knowledge.themeName = theme.themeName
                    knowledge.subThemeName = subTheme.themeName
                    knowledge_list.append(knowledge)
        logger.info(f"{len(courseThemeList)} themes, {len(knowledge_list)} knowledge points")

        ctx = ObjDict({
            "courseId": courseId,
            "classId": classId,
            "basic": basic,
            "themes": courseThemeList,
            "knowledgeList": knowledge_list,
            "accessKeys": ObjDict(default=None),
            "cookies": self.session.cookies.copy(),
            "headers": self.session.headers.copy(),
            "fucked_time": 0
        }, default={})
        self.context[key] = ctx
        return ctx

    def smartQuery(self, path: str, data: dict, ok_code: int = 200, method: str = "POST"):
        """### query smart course API, auto encrypt with AI_KEY"""
        self._checkCookies()
        url = path if path.startswith("http") else SMART_BASE + path
        return self.zhidaoQuery(url, data, ok_code=ok_code, key=AI_KEY,
                                contentType="json", method=method)

    def listSmartNodeResources(self, courseId, classId, knowledgeId, shareCourseId: str = ""):
        """### 取得知识点下的资源列表（带学习状态）"""
        data = {"courseId": courseId, "classId": classId, "knowledgeId": knowledgeId}
        if shareCourseId:
            data["shareCourseId"] = shareCourseId
        return self.smartQuery("/resources/list-knowledge-resource", data).data

    def getSmartResourceDetail(self, courseId, classId, knowledgeId, resourcesUid, fileId=None):
        """### 取得某个资源的详情（视频分段、书籍正文等）"""
        data = {"courseId": courseId, "classId": classId,
                "knowledgeId": knowledgeId, "resourcesUid": resourcesUid}
        if fileId is not None:
            data["fileId"] = fileId
        return self.smartQuery("/resources/get-node-resources-detail", data).data

    def getSmartVideoTime(self, courseId, classId, videoIds: list):
        """### 取得视频总长度，返回 {videoId: 秒}"""
        r = self.smartQuery("/resources-lab/get-video-time",
                            {"courseId": courseId, "classId": classId,
                             "videoIdList": [smartInt(v) for v in videoIds]}).data
        times = ObjDict(default=0)
        for v in r or []:
            times[str(v.videoId)] = int(v.time or 0)
        return times

    def getSmartKnowledgeVideoTime(self, courseId, classId, knowledgeId):
        """### 取得知识点下每个资源已观看的秒数，返回 {resourcesUid: 秒}"""
        r = self.smartQuery("/studyRecord/get-knowledge-video-time",
                            {"courseId": courseId, "classId": classId,
                             "knowledgeId": knowledgeId}).data
        times = ObjDict(default=0)
        for k, v in (r or {}).items():
            times[str(k)] = int(v or 0)
        return times

    def getSmartAccessKey(self, courseId, classId, knowledgeId):
        """### 取得学习凭证 accessKey，上报进度时使用"""
        data = {"courseId": courseId, "keyId": knowledgeId, "knowledgeId": knowledgeId,
                "classId": classId, "type": "MAP", "uuid": self.uuid}
        try:
            return self.smartQuery("/knowledge-study/get-access-key", data).data.accessKey
        except Exception as e:
            logger.error(f"Failed to get access key: {e}")
            return ""

    def getSmartWatchUId(self, fileId):
        """
        ### 取得视频观看凭证 watchUId
        播放器初始化接口返回的 uuid 即可作为 watchUId 使用，同时返回视频地址
        """
        try:
            r = self.session.get("https://newbase.zhihuishu.com/video/initVideoNew",
                                 params={"videoID": str(fileId)},
                                 proxies=self.proxies, timeout=10)
            result = ObjDict(json.loads(r.text)).result
            url = ""
            for line in result.lines or []:
                if line.lineUrl:
                    url = line.lineUrl
                    break
            return result.uuid, url
        except Exception as e:
            logger.error(f"Failed to get watchUId of video {fileId}: {e}")
            return str(int(time.time()*1000)), ""

    def reportSmartVideoProcess(self, courseId, classId, fileId, knowledgeId, lastWatchTime,
                                studyTotalTime: int = 10, shareCourseId: str = "", nodeType: int = 0,
                                watchUId=1):
        """
        ### 上报智慧课程视频观看进度
        * lastWatchTime: 当前播放位置（秒）
        * studyTotalTime: 本轮学习时长（秒），网页端每 10 秒固定上报 10
        """
        data = {
            "courseId": courseId,
            "classId": classId,
            "fileId": smartInt(fileId),
            "studyTotalTime": max(int(studyTotalTime), 1),
            "lastWatchTime": int(lastWatchTime),
            "knowledgeId": knowledgeId,
            "shareCourseId": shareCourseId or "",
            "watchUId": watchUId if watchUId not in (None, "") else 1,
            "nodeType": nodeType,
        }
        return self.smartQuery("/studyRecord/report", data).data

    def saveSmartStudy(self, courseId, classId, knowledgeId, resourcesUid=None, fileId=None,
                       studyTime=None, lastWatchTime=None, studyFileType: int = 1):
        """
        ### 上报智慧课程学习记录
        * studyTime: 累计学习时长（秒），视频进度上报累计值（不是增量）
        * studyFileType: 1 视频，2 其他资源
        """
        data = {
            "courseId": courseId,
            "classId": classId,
            "knowledgeId": knowledgeId,
            "source": 1,
            "studyFileType": studyFileType,
        }
        if resourcesUid is not None:
            data["resourceId"] = resourcesUid
        if fileId is not None:
            data["fileId"] = smartInt(fileId)
        if studyTime is not None:
            data["studyTime"] = round(float(studyTime), 6)
        if lastWatchTime is not None:
            data["lastWatchTime"] = int(lastWatchTime)
        return self.smartQuery("/studyRecord/study", data).data

    def completeSmartResource(self, courseId, classId, knowledgeId, resourcesUid, fileId=None):
        """### 将智慧课程资源标记为已完成（对视频无效，视频必须上报观看进度）"""
        data = {"courseId": courseId, "classId": classId, "knowledgeId": knowledgeId,
                "resourcesUid": resourcesUid, "watchUId": 1}
        if fileId is not None:
            data["fileId"] = smartInt(fileId)
        return self.smartQuery("/studyRecord/completed", data).data

    def isSmartCourseEnded(self, courseId, classId):
        """### 课程学习是否已截止"""
        try:
            return bool(self.smartQuery("/class/is-end-study",
                                        {"courseId": courseId, "classId": classId}).data)
        except Exception:
            return False

    def querySmartExam(self, courseId, classId, knowledgeId):
        """### 查询知识点测验信息"""
        return self.smartQuery("/knowledge-study/query-knowledge-free-exam",
                               {"courseId": courseId, "classId": classId,
                                "knowledgeId": knowledgeId}, ok_code=None)

    def getSmartExamPaper(self, courseId, classId, knowledgeId):
        """
        ### 取得知识点的练习试卷（每次调用会创建一个新的练习）
        返回 {examTestId, paperId, questionNum, masteryScore, ...}，没有练习时 examTestId 为 null
        """
        data = {"scMapId": courseId, "courseId": courseId, "classId": classId,
                "knowledgeId": knowledgeId}
        try:
            return self.smartQuery("/exam/questions-paper", data, ok_code=None).data
        except Exception as e:
            logger.error(f"Failed to get smart exam paper: {e}")
            return None

    def getSmartCourseMapUid(self, courseId):
        """### 取得课程 mapUid / mapName（AI 问答需要）"""
        try:
            r = self.smartQuery("https://kg-ai-run.zhihuishu.com/run/gateway/t/common/course/get-course-mapUid",
                                {"courseId": courseId}).data
            if r and r.get("mapUid"):
                return r.get("mapUid") or "", r.get("mapName") or ""
        except Exception as e:
            logger.debug(f"Failed to get course mapUid: {e}")
        # 兜底：从课程列表里找
        try:
            for c in self.getSmartCourseList():
                if str(c.get("courseId")) == str(courseId) and c.get("mapUid"):
                    return c.get("mapUid") or "", c.get("courseName") or ""
        except Exception as e:
            logger.debug(f"Failed to get mapUid from course list: {e}")
        return "", ""

    def getSmartExamState(self, examTestId, examPaperId):
        """### 取得练习状态（0 未开始 / 1 进行中 / 3 进行中 / 6 已提交）"""
        try:
            r = self.zhidaoAiExamQuery(
                SMART_EXAM_BASE + "/exam/user/getExamTestUserInfo",
                {"examTestId": examTestId, "examPaperId": examPaperId},
                ok_code=0, key=EXAM_KEY, method="GET")
            return (r.get("data") or {}).get("examState")
        except Exception as e:
            logger.error(f"Failed to get smart exam state: {e}")
            return None

    def getSmartKnowledgeMastery(self, courseId, classId, knowledgeId):
        """### 取得知识点的掌握度统计（questionNum/correctNum/mastery/...）"""
        try:
            r = self.smartQuery("/mastery-statistics/get-knowledge-mastery-stat",
                                {"courseId": courseId, "classId": classId,
                                 "knowledgeId": knowledgeId}, ok_code=None)
            return r.get("data") or {}
        except Exception as e:
            logger.error(f"Failed to get mastery stat: {e}")
            return {}

    @staticmethod
    def smartQuestionAnswer(question) -> str:
        """### 从题库接口返回的题目里取出正确答案（选项 id 或填空文本）"""
        options = [o for o in (question.get("optionVos") or []) if o.get("isCorrect") == 1]
        if not options:
            return ""
        if question.get("questionType") == 3:
            return re.sub(r"<[^>]+>", "", str(options[0].get("content") or "")).strip()
        return '#@#'.join(str(o["id"]) for o in options)

    def harvestSmartExamAnswers(self, courseId, classId, knowledgeId, examTestId=0,
                                maxRounds: int = 40, patience: int = 6):
        """
        ### 直接捞取知识点练习的题库答案
        /mastery-statistics/bd/get-test-question 与 /mastery-statistics/get-test-question
        会随机返回若干题目且带 isCorrect 标记，多刷几次能把题库答案基本捞全，
        这样一次运行就能把练习做到满分，不必靠反复提交试错。
        """
        bank = {}
        idle = 0
        paths = ("/mastery-statistics/bd/get-test-question",
                 "/mastery-statistics/get-test-question")
        for _ in range(maxRounds):
            fresh = 0
            for path in paths:
                try:
                    ret = self.smartQuery(path, {"examTestId": examTestId or 0,
                                                 "courseId": courseId, "classId": classId,
                                                 "knowledgeId": knowledgeId}, ok_code=None)
                except Exception as e:
                    logger.debug(f"Harvest {path} failed: {e}")
                    continue
                for question in ((ret.get("data") or {}).get("questionList") or []):
                    qid = str(question.get("id") or "")
                    if not qid or qid in bank:
                        continue
                    answer = self.smartQuestionAnswer(question)
                    if answer:
                        bank[qid] = (question, answer)
                        fresh += 1
            if fresh:
                idle = 0
            else:
                idle += 1
                if idle >= patience:
                    break
        logger.info(f"Harvested {len(bank)} answers for knowledge {knowledgeId}")
        return bank

    def saveSmartAnswerBank(self, courseId, examTestId, bank: dict):
        """### 把捞到的题库答案合并写入 aiexamAnswer 缓存"""
        if not bank:
            return
        path = getRealPath(f"aiexamAnswer/{courseId}/{examTestId}.json")
        os.makedirs(os.path.dirname(path), exist_ok=True)
        cache = {}
        if os.path.exists(path):
            try:
                with open(path, "r", encoding="utf-8") as f:
                    cache = json.load(f)
            except Exception:
                cache = {}
        for qid, (question, answer) in bank.items():
            version = question.get("version", 1)
            key = str(qid) if str(version) == "1" else f"{qid}_{version}"
            options = [{"id": option.get("id"), "content": option.get("content")}
                       for option in (question.get("optionVos") or [])
                       if option.get("isCorrect") == 1]
            cache[key] = {
                "version": version,
                "question": question.get("content", ""),
                "answer": answer,
                "answer_content": "",
                "options": options,
                "hash": ExamCtx.questionHash(question.get("content", "")),
                "questionDict": {},
            }
        with open(path, "w", encoding="utf-8") as f:
            json.dump(cache, f, ensure_ascii=False, indent=4)

    def fuckSmartExam(self, courseId, classId, knowledge, aiConfig: dict = None,
                      maxAttempts: int = SMART_EXAM_MAX_ATTEMPTS, targetMastery: int = SMART_EXAM_TARGET):
        """
        ### 刷智慧课程知识点的练习测试（提升掌握度）
        网页端的练习没有公开答案接口，因此按“作答 -> 提交 -> 读取正确答案 -> 再练习”的方式刷：
        * 首次没有缓存时使用启发式/随机作答
        * 提交后学生端接口会返回每道题的正确选项，答案会写入 aiexamAnswer 缓存
        * 再次练习时优先使用缓存答案，通常一次即可满分
        * aiConfig.enabled 且配置了可用的 OpenAI key 时，会优先用 AI 作答
        """
        knowledgeId = knowledge.knowledgeId
        name = knowledge.knowledgeName
        aiConfig = aiConfig or {}

        # AI 作答开关：智到内置 AI（dify 工作流）或自配 OpenAI 任一可用即可
        opConf = aiConfig.get("openai", {}) or {}
        useZhidao = bool(aiConfig.get("enabled")) and bool(aiConfig.get("use_zhidao_ai", False)) \
            and aiConfig.get("exam_use_ai", False)
        useOpenai = bool(aiConfig.get("enabled")) and not aiConfig.get("use_zhidao_ai", False) \
            and str(opConf.get("api_key", "")).strip() not in ("", "sk-")
        examAI = dict(aiConfig)
        examAI["enabled"] = bool(useZhidao or useOpenai)
        mapUid, mapName = self.getSmartCourseMapUid(courseId)

        best = 0
        harvested = False
        ctx = self.context.get(f"smart_{courseId}_{classId}")
        attempt_begin = time.time()
        for attempt in range(1, maxAttempts + 1):
            try:
                stat = self.getSmartKnowledgeMastery(courseId, classId, knowledgeId)
                mastery = max(int(stat.get("mastery") or 0), int(stat.get("masteryHigh") or 0))
                best = max(best, mastery)
                if mastery >= targetMastery:
                    logger.info(f"Mastery of {name} already {mastery}, skip exam")
                    return best

                meta = self.getSmartExamPaper(courseId, classId, knowledgeId)
                if not meta or not meta.get("examTestId") or not meta.get("paperId"):
                    logger.info(f"No exam available for knowledge {name}")
                    return best

                examTestId, paperId = meta.examTestId, meta.paperId
                # 先从题库接口把答案捞全，避免靠反复试错
                if not harvested:
                    try:
                        bank = self.harvestSmartExamAnswers(courseId, classId, knowledgeId, examTestId)
                        self.saveSmartAnswerBank(courseId, examTestId, bank)
                    except Exception as e:
                        logger.error(f"Failed to harvest answers for {name}: {e}")
                    harvested = True
                state = self.getSmartExamState(examTestId, paperId)
                logger.info(f"Fucking smart exam {name}, attempt {attempt}, "
                            f"paper {paperId}, state {state}")
                examCtx = ExamCtx(fucker=self, courseId=courseId, knowledgeId=knowledgeId,
                                  examTestId=examTestId, examPaperId=paperId,
                                  progress_view=self.progressbar_view, aiConfig=examAI,
                                  opExtra={"courseName": mapName or getattr(knowledge, "themeName", ""),
                                           "knowledgePoint": name,
                                           "mapUid": mapUid, "scMapUid": str(courseId)},
                                  skipOpen=state == 6)
                ok, correct, total = examCtx.startFuck()
                stat = self.getSmartKnowledgeMastery(courseId, classId, knowledgeId)
                mastery = max(int(stat.get("mastery") or 0), int(stat.get("masteryHigh") or 0))
                best = max(best, mastery)
                logger.info(f"Smart exam {name} attempt {attempt}: {correct}/{total}, mastery {mastery}")
                if mastery >= targetMastery or (total and correct >= total):
                    break
                if ctx is not None:
                    ctx.fucked_time += int(time.time() - attempt_begin)
                attempt_begin = time.time()
                time.sleep(2)
            except Exception as e:
                logger.exception(e)
                logger.error(f"Failed to fuck smart exam {name}: {e}")
                try:
                    examCtx.examStopped = True
                except Exception:
                    pass
                break
        return best

    @staticmethod
    def smartResourceKind(resource: dict) -> str:
        """
        ### 判断智慧课程资源类型
        返回 video / ppt / file / ebook / img / mp3 / link / other
        """
        r = ObjDict(resource, default=None)
        if r.resourcesDataType in (12, 23) and r.resourcesChannel != 7:
            return "link"
        if r.resourcesDataType == 22:
            return "video"
        if r.resourcesDataType == 21:
            return "ebook"
        if r.resourcesChannel == 7:
            return "img"
        suffix = (r.resourcesSuffix or "").lower()
        if not suffix:
            url = r.resourcesUrl or ""
            suffix = url.split("?")[0].rsplit(".", 1)[-1].lower() if "." in url else ""
        if suffix in ("jpg", "jpeg", "png", "gif", "svg", "tif", "wmf", "hdr", "dxf", "psd", "tga", "bmp", "webp", "mpg"):
            return "img"
        if suffix in ("ppt", "pptx"):
            return "ppt"
        if suffix in ("mp4", "mpeg2", "wmv", "avi", "flv", "mov", "svga", "apng", "flash", "m4v", "asf",
                      "rm", "rmvb", "ram", "mpeg", "3gp", "dvix", "dv", "mkv", "vob", "qt", "divx", "cpk", "fli", "flc", "mod"):
            return "video"
        if suffix in ("mp3", "wav", "wma", "aac", "m4a"):
            return "mp3"
        if suffix in ("txt", "doc", "docx", "xls", "xlsx", "csv", "pdf", "ebook"):
            return "file"
        return "other"

    def fuckSmartVideo(self, courseId, classId, knowledge, resource, shareCourseId: str = ""):
        """
        ### 刷智慧课程视频
        * knowledge: 知识点（含 knowledgeId / knowledgeName）
        * resource: 资源项（含 resourcesDetail / studyStatus / schedule）
        """
        detail = ObjDict(resource.resourcesDetail, default=None)
        knowledgeId = knowledge.knowledgeId
        resourcesUid = detail.resourcesUid
        # 个别资源只有 fileIdStr（例如引用的外部视频），两种都要兼容
        fileId = detail.resourcesFileId or detail.resourcesFileIdStr
        fileIdStr = detail.resourcesFileIdStr
        name = detail.resourcesName

        # 视频分段信息
        info = self.getSmartResourceDetail(courseId, classId, knowledgeId, resourcesUid, fileId)
        segments = ((info or {}).get("resourcesVideoDetail") or {}).get("videoSegList") or []
        if segments:
            segStart = int(segments[0].videoSegStartTime or 0) / 1000.0
            segEnd = int(segments[0].videoSegEndTime or 0) / 1000.0
        else:
            segStart, segEnd = 0.0, float(detail.resourcesTime or 0)
        if segEnd <= 0:
            for vid in (fileId, fileIdStr):
                if not vid:
                    continue
                try:
                    segEnd = float(self.getSmartVideoTime(courseId, classId, [vid]).get(str(vid)) or 0)
                except Exception:
                    segEnd = 0
                if segEnd > 0:
                    fileId = vid
                    break
        if segEnd <= 0:
            logger.error(f"unknown video length of {name} (fileId={fileId}, fileIdStr={fileIdStr})")
            raise ValueError(f"unknown video length: {name}")

        # 已经看过的位置
        try:
            watched = float(self.getSmartKnowledgeVideoTime(courseId, classId, knowledgeId).get(str(resourcesUid)) or 0)
        except Exception:
            watched = 0.0
        played = max(segStart, watched)
        end_time = max(segStart + (segEnd - segStart) * self.end_thre, segStart + 1.0)

        if played >= end_time or (resource.schedule or 0) >= 85:
            # 差一点就完成（或服务端没收到最后一次上报）时，补一条上报把它顶完，而不是直接跳过
            try:
                final = max(played, end_time)
                self.saveSmartStudy(courseId, classId, knowledgeId, resourcesUid, fileId,
                                    studyTime=final, lastWatchTime=int(final))
                self.reportSmartVideoProcess(courseId, classId, fileId, knowledgeId,
                                             int(final), max(int(SMART_REPORT_INTERVAL), 1), shareCourseId)
                logger.info(f"Video {name} near finished ({played:.0f}/{segEnd:.0f}), sent final report")
            except Exception as e:
                logger.error(f"Failed to finish smart video {name}: {e}")
            return

        # 模拟打开播放器（顺手取一次视频地址；上报用的 watchUId 固定为 1，不需要 uuid）
        try:
            watchUId, videoUrl = self.getSmartWatchUId(fileId)
        except Exception:
            videoUrl = ""
        if videoUrl:
            logger.debug(f"smart video url: {videoUrl}")

        # 少数资源详情会带 watchUId，优先使用，没有则用官方固定值 1
        watchUId = (info or {}).get("watchUId")
        if not watchUId:
            inner = (info or {}).get("resourcesDetail") or {}
            watchUId = inner.get("watchUId")
        watchUId = watchUId or 1

        speed = self.speed or SMART_DEFAULT_SPEED
        if speed > SMART_MAX_SPEED:
            logger.warning(f"Speed {speed}x exceeds safe limit for smart course, clamp to {SMART_MAX_SPEED}x")
            speed = SMART_MAX_SPEED
        report_interval = SMART_REPORT_INTERVAL
        last_report = played
        begin_time = time.time()
        logger.info(f"Fucking smart video {name} ({fileId}) {played:.0f}/{end_time:.0f}s, speed={speed}")
        ctx = self.context.get(f"smart_{courseId}_{classId}")
        while played < end_time:
            time.sleep(1)
            if ctx is not None:
                ctx.fucked_time += 1
                if ctx.fucked_time % 30 == 0:  # 视频较长时也能及时响应 -l 限制
                    self._checkTimeLimit(f"smart_{courseId}_{classId}")
            played = min(played + speed, end_time)
            if played - last_report >= report_interval or played >= end_time:
                try:
                    self.saveSmartStudy(courseId, classId, knowledgeId, resourcesUid, fileId,
                                        studyTime=played, lastWatchTime=int(played))
                    self.reportSmartVideoProcess(courseId, classId, fileId, knowledgeId,
                                                 int(played), int(played - last_report) or 1,
                                                 shareCourseId)
                except Exception as e:
                    logger.error(f"Failed to report progress of video {name}: {e}")
                last_report = played
                progressBar(played, end_time, prefix=f"fucking {fileId}",
                            suffix="done", progressbar_view=self.progressbar_view)
        # 收尾：把最后一段进度补齐
        try:
            self.saveSmartStudy(courseId, classId, knowledgeId, resourcesUid, fileId,
                                studyTime=played, lastWatchTime=int(played))
            self.reportSmartVideoProcess(courseId, classId, fileId, knowledgeId,
                                         int(played), max(int(report_interval), 1), shareCourseId)
        except Exception as e:
            logger.error(f"Failed to finish smart video {name}: {e}")
        # 校验是否真的完成；未完成则用 initVideoNew 的 uuid 作为 watchUId 再补几次
        try:
            status = None
            for r in (self.listSmartNodeResources(courseId, classId, knowledgeId, shareCourseId).resourceList or []):
                if str(r.resourcesDetail.resourcesUid) == str(resourcesUid):
                    status = r.studyStatus
                    break
            if status != 1:
                alt_uid, _ = self.getSmartWatchUId(fileId)
                logger.warning(f"Video {name} not completed yet, retry with watchUId={alt_uid}")
                for _ in range(3):
                    self.saveSmartStudy(courseId, classId, knowledgeId, resourcesUid, fileId,
                                        studyTime=end_time, lastWatchTime=int(end_time))
                    self.reportSmartVideoProcess(courseId, classId, fileId, knowledgeId,
                                                 int(end_time), report_interval, shareCourseId,
                                                 watchUId=alt_uid)
                    time.sleep(0.5)
        except Exception as e:
            logger.error(f"Failed to verify video {name}: {e}")
        logger.info(f"Fucked smart video {name}, cost {time.time()-begin_time:.1f}s")

    def fuckSmartResource(self, courseId, classId, knowledge, resource, shareCourseId: str = ""):
        """### 刷智慧课程的单个资源（按类型分派）"""
        detail = ObjDict(resource.resourcesDetail, default=None)
        kind = self.smartResourceKind(dict(detail))
        name = detail.resourcesName
        knowledgeId = knowledge.knowledgeId
        resourcesUid = detail.resourcesUid
        fileId = detail.resourcesFileId

        if kind == "video":
            return self.fuckSmartVideo(courseId, classId, knowledge, resource, shareCourseId)

        # 非视频资源：直接标记完成，与网页行为一致
        ctx = self.context.get(f"smart_{courseId}_{classId}")
        if ctx is not None:
            ctx.fucked_time += 1
        self.completeSmartResource(courseId, classId, knowledgeId, resourcesUid, fileId)
        self.saveSmartStudy(courseId, classId, knowledgeId, resourcesUid,
                            studyFileType=2)
        logger.info(f"Fucked smart resource {name} ({kind})")

    def _sweepSmartCourse(self, courseId, classId, tprint, prefix, w_lim,
                          shareCourseId: str = "", rounds: int = 2):
        """
        ### 第一遍刷完后补漏
        视频进度上报存在服务端异步/偶发丢失，单遍运行偶尔会留下 0% 的资源；
        这里重新拉取课程状态，把仍未完成的资源再刷一遍。
        """
        cid = f"smart_{courseId}_{classId}"
        for rnd in range(1, rounds + 1):
            self._checkTimeLimit(cid)
            try:
                ctx = self.getSmartCourseContext(courseId, classId, force=True)
            except Exception as e:
                logger.error(f"Failed to refresh smart course context: {e}")
                return
            pending = 0
            for knowledge in ctx.knowledgeList:
                if (knowledge.studyProgress or 0) >= 100:
                    continue
                try:
                    resources = self.listSmartNodeResources(courseId, classId,
                                                            knowledge.knowledgeId, shareCourseId)
                except Exception as e:
                    logger.error(f"Failed to refresh resources of {knowledge.knowledgeName}: {e}")
                    continue
                todo = [r for r in (resources.resourceList or []) if r.studyStatus != 1]
                if not todo:
                    continue
                pending += len(todo)
                tprint(f"{prefix}__Retry({rnd}) {knowledge.knowledgeName} ({len(todo)} left)"[:w_lim])
                for resource in todo:
                    self._checkTimeLimit(cid)
                    name = ObjDict(resource.resourcesDetail, default=None).resourcesName
                    tprint(f"{prefix*2}__Fucking {name}"[:w_lim])
                    try:
                        self.fuckSmartResource(courseId, classId, knowledge, resource, shareCourseId)
                    except TimeLimitExceeded:
                        raise
                    except Exception as e:
                        logger.exception(e)
                        tprint(f"{prefix*2}##Failed: {e}"[:w_lim])
            if pending == 0:
                logger.info(f"Smart course sweep round {rnd}: nothing left")
                break

    def _sweepSmartExams(self, courseId, classId, aiConfig, tprint, prefix, w_lim, maxExamAttempts):
        """
        ### 补漏：对掌握度仍然偏低的知识点再补几轮练习
        （单题题库最高只能是 94，所以用 90 作为补漏阈值，避免无意义重刷）
        """
        cid = f"smart_{courseId}_{classId}"
        try:
            ctx = self.getSmartCourseContext(courseId, classId, force=True)
        except Exception as e:
            logger.error(f"Failed to refresh smart course context: {e}")
            return
        for knowledge in ctx.knowledgeList:
            if knowledge.freeExam not in (0, "0"):
                continue
            if (knowledge.masteryPercentage or 0) >= 90:
                continue
            self._checkTimeLimit(cid)
            tprint(f"{prefix}__Retry exam {knowledge.knowledgeName} (mastery {knowledge.masteryPercentage})"[:w_lim])
            try:
                self.fuckSmartExam(courseId, classId, knowledge, aiConfig,
                                   maxAttempts=min(3, maxExamAttempts))
            except TimeLimitExceeded:
                raise
            except Exception as e:
                logger.exception(e)
                tprint(f"{prefix}##Exam retry failed: {e}"[:w_lim])

    def fuckSmartCourse(self, courseId, classId, tree_view: bool = None, shareCourseId: str = "",
                        aiConfig: dict = None, no_exam: bool = False,
                        maxExamAttempts: int = SMART_EXAM_MAX_ATTEMPTS):
        """
        ### 刷完整个智慧课程
        * courseId: 课程 ID
        * classId: 班级 ID
        * aiConfig: AI 配置，用于练习测试自动作答
        * no_exam: 跳过知识点练习测试
        """
        tree_view = self.tree_view if tree_view is None else tree_view
        ctx = self.getSmartCourseContext(courseId, classId)
        course = ctx.basic
        tprint = print if tree_view else (lambda *a, **k: None)
        prefix = self.prefix
        begin_time = time.time()
        try:
            w_lim = os.get_terminal_size().columns - 1
        except Exception:
            w_lim = 80

        courseName = (course or {}).get("courseName") or f"{courseId}/{classId}"
        logger.info(f"Fucking smart course {courseName} ({courseId}/{classId})")
        tprint(f"Fucking smart course: {courseName}")
        cid = f"smart_{courseId}_{classId}"

        try:
            for theme in ctx.themes:
                tprint(prefix)
                tprint(f"{prefix}__Fucking theme {theme.themeName}"[:w_lim])
                for subTheme in theme.subThemeList or []:
                    knowledgeList = subTheme.knowledgeList or []
                    if not knowledgeList:
                        continue
                    tprint(f"{prefix*2}__Theme {subTheme.themeName}"[:w_lim])
                    for knowledge in knowledgeList:
                        self._checkTimeLimit(cid)
                        tprint(f"{prefix*3}__Knowledge {knowledge.knowledgeName}"[:w_lim])
                        needStudy = not (knowledge.studyProgress and knowledge.studyProgress >= 100)
                        needExam = (not no_exam) and knowledge.freeExam in (0, "0") \
                            and (knowledge.masteryPercentage or 0) < 95
                        if not needStudy and not needExam:
                            tprint(f"{prefix*4}##already fucked ({knowledge.studyProgress}%)")
                            continue
                        if needStudy:
                            try:
                                resources = self.listSmartNodeResources(courseId, classId,
                                                                        knowledge.knowledgeId, shareCourseId)
                            except Exception as e:
                                logger.exception(e)
                                tprint(f"{prefix*4}##Failed to get resources: {e}"[:w_lim])
                                resources = None
                            for resource in (resources.resourceList if resources else []) or []:
                                detail = ObjDict(resource.resourcesDetail, default=None)
                                if resource.studyStatus == 1:
                                    tprint(f"{prefix*4}##{detail.resourcesName} already fucked")
                                    continue
                                tprint(f"{prefix*4}__Fucking {detail.resourcesName}"[:w_lim])
                                try:
                                    self.fuckSmartResource(courseId, classId, knowledge, resource, shareCourseId)
                                except TimeLimitExceeded:
                                    raise
                                except Exception as e:
                                    logger.exception(e)
                                    tprint(f"{prefix*4}##Failed: {e}"[:w_lim])
                        # 知识点练习（提升掌握度）：有练习且最高掌握度未达标时才做
                        if needExam:
                            try:
                                self.fuckSmartExam(courseId, classId, knowledge, aiConfig,
                                                   maxAttempts=maxExamAttempts)
                            except Exception as e:
                                logger.exception(e)
                                tprint(f"{prefix*4}##Exam failed: {e}"[:w_lim])
                        tprint(f"{prefix*3}__Fucked knowledge point {knowledge.knowledgeName}"[:w_lim])
            # 第一遍结束后补漏，保证一次运行尽量跑满
            self._sweepSmartCourse(courseId, classId, tprint, prefix, w_lim, shareCourseId)
            if not no_exam:
                self._sweepSmartExams(courseId, classId, aiConfig, tprint, prefix, w_lim, maxExamAttempts)
        except TimeLimitExceeded as e:
            logger.info(f"Fucking time limit exceeded: {e}")
            self._pushplus("fuckZHS", "刷课已完成")
            self._bark("fuckZHS", "刷课已完成")
            tprint(prefix)
            tprint(f"{prefix}##Fucking time limit exceeded: {e}\n")
        except KeyboardInterrupt:
            logger.info("User interrupted")
            tprint(f"{prefix}##Interrupted")

        wipeLine()
        tprint(prefix)
        tprint(f"{prefix}__Fucked smart course {courseName}, cost {time.time()-begin_time:.2f}s")


class ExamCtx:
    def __init__(self, fucker: Fucker, courseId: int, knowledgeId: int, examTestId: int, examPaperId: int, progress_view: bool = True, aiConfig: dict = {}, opExtra: dict = {}, skipOpen: bool = False):
        self.fucker = fucker
        self.courseId = courseId
        self.examTestId = examTestId
        self.examPaperId = examPaperId
        self.knowledgeId = knowledgeId
        self.opExtra = opExtra
        self.aiConfig = aiConfig
        self.progress_view = progress_view
        self.skipOpen = skipOpen

        self.answerCache = {}
        self.allAnswerCache = {} # 存储同课程所有题目的答案
        self.sheetContent = None
        self.referenceMaterials = []
        self.timeUpdateIndex = 0
        self.examStopped = False

        if aiConfig.get("enabled", False) and not aiConfig.get("use_zhidao_ai", False):
            opConf: dict = aiConfig.get("openai", {})
            self.op = Openai(
                baseUrl=opConf.get("api_base", "https://api.openai.com/v1"),
                apiKey=opConf.get("api_key", ""),
                modelName=opConf.get("model_name", "davinci"),
                stream=aiConfig.get("use_stream", False),
                extra=opExtra,
            )

        if aiConfig.get("enabled", False) and aiConfig.get("use_zhidao_ai", False):
            session = requests.Session()
            session.cookies.update(fucker.session.cookies)
            session.headers.update(fucker.session.headers)
            session.proxies.update(fucker.proxies)
            self.op = Openai(
                useZhidao=True,
                zhiDaosession=session,
                stream=aiConfig.get("use_stream", False),
                extra=opExtra,
            )

    def getAnswerpath(self, examTestId):
        answerpath = getRealPath(
            f"aiexamAnswer/{self.courseId}/{examTestId}.json")

        # 确保目录存在
        os.makedirs(os.path.dirname(answerpath), exist_ok=True)

        # 如果文件不存在，创建一个包含空字典的 JSON 文件
        if not os.path.exists(answerpath):
            with open(answerpath, "w", encoding="utf-8") as f:
                json.dump({}, f)

        return answerpath
    
    def getAllAnswerpath(self): # 同课程所有题目的答案
        answerpath = getRealPath(
            f"aiexamAnswer/{self.courseId}/data.json")

        # 确保目录存在
        os.makedirs(os.path.dirname(answerpath), exist_ok=True)

        # 如果文件不存在，创建一个包含空字典的 JSON 文件
        if not os.path.exists(answerpath):
            with open(answerpath, "w", encoding="utf-8") as f:
                json.dump({}, f)

        return answerpath

    def readAnswerCache(self, examTestId):
        Allanwerpath = self.getAllAnswerpath()
        path = getRealPath(f"aiexamAnswer/{self.courseId}/")
        files = os.listdir(path)
        Allcache = {}
        for file in files:
            if file == "data.json":
                continue
            file_path = os.path.join(path, file)
            with open(file_path, "r", encoding="utf-8") as f:
                cache = json.load(f)
                Allcache.update(cache)
        
        self.allAnswerCache = {}
        for key, value in Allcache.items():
            if '_' in key:
                questionId, version = key.split('_')
                self.allAnswerCache[f"{questionId}_{version}"] = value
            else:
                self.allAnswerCache[key] = value
                # 为没有版本号的答案添加默认版本
                value['version'] = 1


        answerpath = self.getAnswerpath(examTestId)
        with open(answerpath, "r", encoding="utf-8") as f:
            cache = json.load(f)

        # 转换缓存格式以支持版本号
        self.answerCache = {}
        for key, value in cache.items():
            if '_' in key:
                questionId, version = key.split('_')
                self.answerCache[f"{questionId}_{version}"] = value
            else:
                self.answerCache[key] = value
                # 为没有版本号的答案添加默认版本
                value['version'] = 1

        return self.answerCache, self.allAnswerCache

    def writeAnswerCacheToDisk(self):
        answerpath = self.getAnswerpath(self.examTestId)
        with open(answerpath, "w", encoding="utf-8") as f:
            json.dump(self.answerCache, f, ensure_ascii=False, indent=4)

        allAnswerpath = self.getAllAnswerpath()
        with open(allAnswerpath, "w", encoding="utf-8") as f:
            json.dump(self.allAnswerCache, f, ensure_ascii=False, indent=4)

    def getAnswer(self, questionId: int, version: int = 1) -> dict | None:
        key = str(questionId) if version == 1 else f"{questionId}_{version}"
        result = self.allAnswerCache.get(key) # 从同课程所有题目的答案中获取
        return result

    @staticmethod
    def questionHash(text) -> str:
        """### 题干哈希，用于跨 questionId 复用答案"""
        plain = re.sub(r"<[^>]+>", "", str(text or "")).strip()
        return hashlib.md5(plain.encode("utf-8")).hexdigest()

    def setAnswer(self, questionId: int, version: int, answer_data: dict):
        question_dict = answer_data.get("questionDict") or {}
        options = [{"id": option.get("id"), "content": option.get("content")}
                   for option in (question_dict.get("optionVos") or [])
                   if option.get("isCorrect") == 1]
        entry = {
            "version": version,
            "question": answer_data.get("question", ""),
            "answer": answer_data.get("answer", ""),
            "answer_content": answer_data.get("answer_content", ""),
            "options": options,
            "hash": self.questionHash(answer_data.get("question", "")),
            "questionDict": answer_data.get("questionDict", {})
        }
        self.answerCache[str(questionId) if version == 1 else f"{questionId}_{version}"] = dict(entry)
        self.allAnswerCache[str(questionId) if version == 1 else f"{questionId}_{version}"] = dict(entry)

        self.writeAnswerCacheToDisk()

    def openExam(self, triedTimes: int = 0):
        url = f"https://studentexamtest.zhihuishu.com/gateway/t/v1/exam/user/openExam"

        data = {
            "examTestId": self.examTestId,
            "examPaperId": self.examPaperId,
            "courseId": self.courseId,
        }
        try:
            ret = self.fucker.zhidaoAiExamQuery(
                url, data, ok_code=0, key=EXAM_KEY, method="POST")

        except Exception as e:
            if triedTimes < 3:
                logger.error(
                    f"openExam failed, retrying... {triedTimes} times")
                return self.openExam(triedTimes + 1)
            else:
                logger.error(f"openExam failed, retried 3 times, giving up...")
                raise e
        # 启动定时更新时间的线程
        threading.Thread(target=self.updateExamCostTime,
                         args=(10,), daemon=True).start()
        return True

    def updateExamCostTime(self, heartbeatTime: int = 10):
        url = "https://studentexamtest.zhihuishu.com/gateway/t/v1/exam/user/updateUserUsedTime"

        data = {
            "examTestId": self.examTestId,
            "examPaperId": self.examPaperId,
            "heartbeatTime": heartbeatTime
        }

        while not self.examStopped:
            try:
                ret = self.fucker.zhidaoAiExamQuery(
                    url, data, ok_code=0, key=EXAM_KEY, method="POST")
            except Exception as e:
                logger.error(f"updateExamCostTime failed: {e}")
            finally:
                self.timeUpdateIndex += 1
                if self.timeUpdateIndex % 10 == 0:
                    logger.info(
                        f"Exam {self.examTestId} cost time: {self.timeUpdateIndex * heartbeatTime}s")

                time.sleep(heartbeatTime)

    def getSheetContent(self, triedTimes: int = 0) -> list:
        if self.sheetContent is not None:
            return self.sheetContent
        url = "https://studentexamtest.zhihuishu.com/gateway/t/v1/exam/user/getExamSheetInfo"

        data = {
            "examTestId": self.examTestId,
            "examPaperId":  self.examPaperId
        }

        try:
            ret = self.fucker.zhidaoAiExamQuery(
                url, data, ok_code=0, key=EXAM_KEY, method="GET")
            parts = ret["data"].get("partSheetVos") or []
            self.sheetContent = [q for part in parts for q in (part.get("questionSheetVos") or [])]
        except Exception as e:
            logger.error(f"getSheetContent failed: {e}")

            if triedTimes < 3:
                logger.error(
                    f"getSheetContent failed, retrying... {triedTimes} times")
                return self.getSheetContent(triedTimes + 1)
            else:
                logger.error(
                    f"getSheetContent failed, retried 3 times, giving up...")
                raise e

        return self.sheetContent

    def getQuestionContent(self, questionId: int, version: int, triedTimes: int = 0) -> dict:
        url = "https://studentexamtest.zhihuishu.com/gateway/t/v1/question/getExamQuestionInfo"
        data = {
            "examTestId": self.examTestId,
            "examPaperId":  self.examPaperId,
            "questionId": questionId,
            "version": version
        }

        try:
            ret = self.fucker.zhidaoAiExamQuery(
                url, data, ok_code=0, key=EXAM_KEY, method="GET")
            return ret["data"]
        except Exception as e:
            if triedTimes < 3:
                logger.error(
                    f"getQuestionContent failed, retrying... {triedTimes} times")
                return self.getQuestionContent(questionId, version, triedTimes + 1)
            else:
                logger.error(
                    f"getQuestionContent failed, retried 3 times, giving up...")
                return None

    def saveAnswer(self, questionId: int, answers: list):
        if not answers:
            return False
        if all(str(a).strip() in ("", "None") for a in answers):
            return False
        url = "https://studentexamtest.zhihuishu.com/gateway/t/v1/answer/saveAnswer"

        data = {
            "recruitId": self.courseId,
            "examTestId": self.examTestId,
            "examPaperId": self.examPaperId,
            "questionId": questionId,
            "dataVos": None,
            "answer": '#@#'.join(str(answer) for answer in answers),
        }

        try:
            ret = self.fucker.zhidaoAiExamQuery(
                url, data, ok_code=0, key=EXAM_KEY, method="POST")
        except Exception as e:
            logger.error(f"saveAnswer failed: {e}")
            return False

        return True

    def submitExam(self, triedTimes: int = 0):
        url = "https://studentexamtest.zhihuishu.com/gateway/t/v1/exam/user/submit"

        data = {
            "examTestId": self.examTestId,
            "courseId": self.courseId,
            "courseType": 8,
            "examPaperId": self.examPaperId,
            "aiKnlowledgeId": self.knowledgeId,
        }

        try:
            ret = self.fucker.zhidaoAiExamQuery(
                url, data, ok_code=0, key=EXAM_KEY, method="POST")
        except Exception as e:
            logger.error(f"submitExam failed: {e}")
            if triedTimes < 3:
                logger.error(
                    f"submitExam failed, retrying... {triedTimes} times")
                return self.submitExam(triedTimes + 1)
            else:
                logger.error(
                    f"submitExam failed, retried 3 times, giving up...")
                raise e

        finally:
            self.examStopped = True

        return True

    def getQuestionAnswer(self, questionDict: dict) -> tuple[list, str] | None:
        questionId = questionDict["id"]
        questionType = questionDict["questionType"]
        version = questionDict.get("version", 1)
        questionContent = questionDict.get("content", "")

        # 选项，只保留有id和content的选项
        choices = [
            {"id": option["id"], "content": option["content"]}
            for option in (questionDict.get("optionVos") or [])
            if "id" in option and "content" in option
        ]

        # 尝试从缓存中获取答案（会自动做一次版本兼容映射）
        entry = self.getAnswer(questionId, version)
        if entry is not None:
            ids = self.resolveCachedAnswer(entry, choices, questionType)
            if ids:
                time.sleep(uniform(0.2, 0.5))
                return ids, "cached"

        # 同一道题换了个 questionId / 版本时，按题干哈希再找一次
        content_hash = self.questionHash(questionContent)
        for item in self.allAnswerCache.values():
            if item.get("hash") != content_hash:
                continue
            ids = self.resolveCachedAnswer(item, choices, questionType)
            if ids:
                time.sleep(uniform(0.1, 0.3))
                return ids, "cached(hash)"

        # 填空客观题（自动批阅）：只有拿到答案文本才能交，交选项 id 必判错
        if questionType not in (1, 2, 14):
            if len(choices) == 1:
                text = re.sub(r"<[^>]+>", "", str(choices[0]["content"]) or "").strip()
                if text:
                    return [text], "fill"
            return None, "unsupported type"

        # 选项数量少于2个（判断/单选等异常情况），能答就答，不能答就跳过
        if not choices:
            return None, "no options"
        if len(choices) < 2:
            return [choices[0]["id"]], "single option"

        try:
            # 选项数量大于2个，使用AI生成答案
            op = self.op

            if questionType == 1:
                # 单选题
                prompt = op.singleChoiceTemplate(questionContent, choices, referenceMaterials=self.referenceMaterials)
            elif questionType == 2:
                # 多选题
                prompt = op.multipleChoiceTemplate(questionContent, choices, referenceMaterials=self.referenceMaterials)
            elif questionType == 14:
                # 判断题
                prompt = op.judgementTemplate(questionContent, choices, referenceMaterials=self.referenceMaterials)
            else:
                raise ValueError(f"Unsupported question type: {questionType}")
            answer = op.generateAnswer(prompt, choices)
            return answer, "AI generated"
        except Exception as e:
            # 没有可用的 AI，使用简单启发式，实在不行再随机
            answer = self.heuristicAnswer(questionType, questionContent, choices)

            time.sleep(uniform(0.1, 0.3))

        return answer, "heuristic"

    @staticmethod
    def stripHtml(text) -> str:
        return re.sub(r"<[^>]+>", "", str(text or "")).strip()

    def resolveCachedAnswer(self, entry: dict, choices: list, questionType: int):
        """
        ### 把缓存答案映射到当前题目的选项上
        题库存在多个版本（选项顺序/内容会变），缓存里是旧版本的选项 id，
        这时按选项内容重新匹配；匹配不上就当作未命中，交给启发式/AI。
        """
        cached = str(entry.get("answer", "") or "")
        if not cached:
            return None
        if questionType == 3:
            return None if re.fullmatch(r"[0-9#@]+", cached) else [cached]
        ids = [i for i in cached.split('#@#') if i]
        valid = {str(c["id"]) for c in choices}
        if ids and all(i in valid for i in ids):
            return ids
        options = entry.get("options") or []
        if not options:
            return None
        mapped = []
        for option in options:
            text = self.stripHtml(option.get("content", ""))
            match = next((c for c in choices if self.stripHtml(c["content"]) == text), None)
            if not match:
                return None
            mapped.append(str(match["id"]))
        return mapped or None

    def heuristicAnswer(self, questionType: int, questionContent: str, choices: list) -> list:
        """
        ### 没有 AI 可用时的兜底答题启发式
        * 判断题：出现“只/就是/一定/全部”等绝对化表述时选错，否则选对
        * 选择题：优先选择“以上都是”类选项，否则随机
        """
        def strip(html):
            return re.sub(r"<[^>]+>", "", str(html or "")).strip()

        text = strip(questionContent)
        texts = [(strip(c["content"]), c["id"]) for c in choices]
        if questionType == 14:
            for t, cid in texts:
                if t in ("错", "错误", "否", "不正确") and re.search(r"(就是|只能|只吃|一定|全部|所有|必须|完全|均|都)", text):
                    return [cid]
            for t, cid in texts:
                if t in ("对", "正确", "是"):
                    return [cid]
            return [texts[0][1]]
        for t, cid in texts:
            if re.search(r"(以上都|以上均|所有以上|上述全|全都正确|以上选项)", t):
                return [cid]
        if questionType == 2:
            return [c["id"] for c in sample(choices, min(2, len(choices)))]
        return [sample(choices, 1)[0]["id"]]

    def select_random_answers(self, choices, n):
        # 确保 n 不大于 choices 的长度
        n = min(n, len(choices))

        # 随机选择 n 个选项
        selected_choices = sample(choices, n)

        # 返回选中选项的 id
        return [choice['id'] for choice in selected_choices]

    def startFuck(self, referenceMaterials: list = [dict(name="参考资料", url="https://www.zhihuishu.com/course/10]", content=str)]) -> tuple[bool, int, int]:
        self.referenceMaterials = referenceMaterials

        # 加载答案缓存
        self.readAnswerCache(self.examTestId)

        # 打开考试（已经开考的不必重复打开，直接开始计时心跳）
        if self.skipOpen:
            threading.Thread(target=self.updateExamCostTime, args=(10,), daemon=True).start()
        else:
            self.openExam()

        # 获取考试试卷内容
        sheetContent = self.getSheetContent()
        if sheetContent is None:
            raise ValueError("sheet has no content")

        # 遍历试卷内容，获取每道题目的答案
        index = 0
        total_questions = len(sheetContent)
        if self.progress_view :
            progressBar(index, total_questions, "fucking exam",
                        suffix=f"{index}/{total_questions}")
        for questionDict in sheetContent:
            # 获取题目内容
            questionContentDict = self.getQuestionContent(
                questionDict["questionId"], questionDict.get("version", 1))

            if questionContentDict is None:
                logger.error(
                    f"getQuestionContent failed: {questionDict['questionId']}")
                continue

            # 获取题目答案
            questionContentDict.version = questionDict.get("version", 1)
            try:
                answer, note = self.getQuestionAnswer(questionContentDict)
            except Exception as e:
                logger.error(f"getQuestionAnswer failed: {questionDict['questionId']} {e}")
                continue

            if answer is None:
                logger.error(
                    f"getQuestionAnswer failed: {questionDict['questionId']}")
                continue

            # 保存答案
            self.saveAnswer(questionDict["questionId"], answer)

            if self.progress_view :
                action = f"fucking exam"
                index += 1
                progressBar(index, total_questions, action,
                            suffix=f"({index}/{total_questions}) {note}")

        # 提交考试
        self.submitExam()

        # 重新取得试卷内容，检查是否答对了，并更新答案缓存
        total_questions = len(sheetContent)
        correct_questions = 0
        for questionDict in sheetContent:
            # 取得版本
            version = questionDict.get("version", 1)
            # 获取题目内容
            questionContentDict = self.getQuestionContent(
                questionDict["questionId"], version)

            if questionContentDict is None:
                logger.error(
                    f"getQuestionContent failed: {questionDict['questionId']}")
                continue

            # 取得做题结果
            result = questionContentDict.get("userAnswerVo", None)
            if result is None:
                logger.error(
                    f"userAnswerVo not found: {questionDict['questionId']}")
                continue
            # 计算得分
            if result[0]["isCorrect"] == 1:
                correct_questions += 1
            else:
                logger.error(
                    f"Question {questionDict['questionId']} is not correct")

            # 获取题目答案
            answer = [{"id": option["id"], "content": option["content"]}
                      for option in questionContentDict["optionVos"]
                      if option.get("isCorrect", 0) == 1]
            if questionContentDict.get("questionType") == 3:
                # 填空客观题缓存文本
                answer_str = '#@#'.join([re.sub(r"<[^>]+>", "", str(option["content"])).strip()
                                        for option in answer])
            else:
                answer_str = '#@#'.join([str(option["id"]) for option in answer])
            answer_content_str = '\n'.join(
                [option["content"] for option in answer])

            # 保存答案
            answer_dict = {
                "question": questionContentDict.get("content", ""),
                "answer": answer_str,
                "answer_content": answer_content_str,
                "questionDict": questionContentDict,
            }
            self.setAnswer(questionDict["questionId"], version, answer_dict)

        # 如果所有题目都做对了，则退出考试
        if correct_questions == total_questions:
            logger.info(
                f"Exam {self.examTestId} is finished, score: {correct_questions}/{total_questions}")
            return True, correct_questions, total_questions
        else:
            logger.info(
                f"Exam {self.examTestId} is not finished, score: {correct_questions}/{total_questions}")
            return False, correct_questions, total_questions

class Openai:
    def __init__(self, baseUrl: str = "", apiKey: str = "", modelName: str = "", useZhidao: bool = False, zhiDaosession: requests.Session = None, stream: bool = False, extra: dict = {}):
        self.baseUrl = baseUrl
        self.apiKey = apiKey
        self.modelName = modelName
        self.extra = extra

        self.stream = stream

        self.session = zhiDaosession if zhiDaosession is not None else requests.Session()
        self.useZhidao = useZhidao

        self.encoder = tiktoken.encoding_for_model("gpt-4")

        self.prefix = "8ZflKEagfL"

    def __parseStream(self, response: requests.Response, aim_start: str, aim_end: str) -> str:
        """解析 stream 响应"""
        cache = ""
        for line in response.iter_lines():
            if not line:
                continue

            try:
                json_data = json.loads(line.decode('utf-8')[5:])
                content = json_data.get("choices", [{}])[0].get(
                    "delta", {}).get("content", "")
                if content:
                    cache += content
                    # 使用正则寻找答案
                    match = re.search(
                        f"{re.escape(aim_start)}(.*?){re.escape(aim_end)}", cache, re.DOTALL)
                    if match:
                        return cache
            except json.JSONDecodeError:
                continue

    def openaiCompletion(self, prompt: str, aimStart: str = "```answer", aimEnd: str = "```", max_retries: int = 3, retry_delay: float = 1.0) -> str:
        url = f"{self.baseUrl}/v1/chat/completions"
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.apiKey}",
        }

        body = {
            "messages": [{"role": "user", "content": prompt}],
            "model": self.modelName,
            "stream": self.stream,
        }

        for attempt in range(max_retries):
            try:
                response = requests.post(
                    url, headers=headers, json=body, timeout=30, stream=self.stream)
                response.raise_for_status()

                if self.stream:
                    result = self.__parseStream(response, aimStart, aimEnd)
                else:
                    result = response.json()

                return result["choices"][0]["message"]["content"] if isinstance(result, dict) else result
            except requests.exceptions.RequestException as e:
                logger.error(
                    f"Completion attempt {attempt + 1} failed: {str(e)}")
                if attempt < max_retries - 1:
                    time.sleep(retry_delay)
                else:
                    logger.error(
                        "All completion attempts failed, giving up...")
                    raise

        # This line should never be reached, but it's here for completeness
        raise Exception("Unexpected error in completion method")

    def zhiDaoCompletion(self, prompt: str, aimStart: str = "```answer", aimEnd: str = "```", max_retries: int = 3, retry_delay: float = 1.0) -> str:
        """
        ### 通过智慧树内置 AI（dify 工作流「AI研习室-助教回答」）作答
        * 旧接口 ai-knowledge-map-platform/.../qa/platform/stream 已下线（返回 509）
        * 需要提供 mapUid / scMapUid（放在 self.extra 里），否则知识库检索为空
        """
        url = "https://kg-dify-proxy.zhihuishu.com/dify/gateway/t/dify/v1"
        body = {
            "response_mode": "streaming",
            "taskName": "AI研习室-助教回答",
            "inputs": {
                "mapUid": self.extra.get("mapUid", ""),
                "scMapUid": self.extra.get("scMapUid", ""),
                "query": prompt,
            },
        }
        payload = {
            "secretStr": Cipher(AI_KEY).encrypt(json.dumps(body, ensure_ascii=False)),
            "date": int(time.time() * 1000),
        }
        last_error = None
        for attempt in range(max_retries):
            try:
                response = self.session.post(
                    url, data=json.dumps(payload), stream=True, timeout=(10, 240),
                    headers={"Accept": "text/event-stream",
                             "Content-Type": "application/json"})
                response.raise_for_status()
                cache = self.__parseDifyStream(response)
                if cache:
                    return cache
                raise ValueError("empty answer from dify workflow")
            except Exception as e:
                last_error = e
                logger.error(f"Completion attempt {attempt + 1} failed: {e}")
                if attempt < max_retries - 1:
                    time.sleep(retry_delay)
        raise Exception(f"zhiDaoCompletion failed: {last_error}")

    @staticmethod
    def __parseDifyStream(response: requests.Response) -> str:
        """### 解析 dify 工作流的 SSE 输出"""
        cache = ""
        for line in response.iter_lines():
            if not line:
                continue
            text = line.decode("utf-8", "replace")
            if not text.startswith("data:"):
                continue
            try:
                event = json.loads(text[5:].strip())
            except json.JSONDecodeError:
                continue
            kind = event.get("event")
            if kind == "text_chunk":
                cache += (event.get("data") or {}).get("text", "")
            elif kind == "workflow_finished":
                outputs = (event.get("data") or {}).get("outputs") or {}
                if not cache and outputs.get("result"):
                    cache = str(outputs["result"])
        return cache

    def __zhiDaoCompletionV1(self, prompt: str, aimStart: str = "```answer", aimEnd: str = "```", max_retries: int = 3, retry_delay: float = 1.0) -> str:
        base_url = "https://ai-knowledge-map-platform.zhihuishu.com/knowledgemap/gateway/t/qa/platform/stream"

        body = {
            "messageList": [{"role": "user", "content": prompt}],
            "modelCode": "moonshot-v1-32k",
            "stream": self.stream,
        }

        url, body = self.__zhidaoSign(base_url, body)

        for attempt in range(max_retries):
            try:
                response = self.session.post(
                    url, json=body, timeout=30, stream=self.stream)
                response.raise_for_status()

                if self.stream:
                    result = self.__parseStream(response, aimStart, aimEnd)
                else:
                    result = json.loads(response.text[5:])

                return result["choices"][0]["message"]["content"] if isinstance(result, dict) else result
            except requests.exceptions.RequestException as e:
                logger.error(
                    f"Completion attempt {attempt + 1} failed: {str(e)}")
                if attempt < max_retries - 1:
                    time.sleep(retry_delay)
                else:
                    logger.error(
                        "All completion attempts failed, giving up...")
                    raise

        # This line should never be reached, but it's here for completeness
        raise Exception("Unexpected error in completion method")

    def __generate_random_session_nid(self):
        chars = string.ascii_lowercase + string.digits
        return "chatcmpl-" + ''.join(random_choice(chars) for _ in range(24))

    def __generate_signature(self, input_string: str) -> str:
        """生成 MD5 签名"""
        return hashlib.md5((self.prefix + input_string).encode('utf-8')).hexdigest()

    def __build_input_string(self, data: dict) -> str:
        """构建输入字符串"""
        json_data = {
            "messageList": "[object Object]",
            "modelCode": data.get("modelCode", ""),
            "sessionNid": data.get("sessionNid", ""),
            "stream": data.get("stream", False)
        }
        return json.dumps(json_data, separators=(',', ':')) \
            .replace('"true"', 'true') \
            .replace('"false"', 'false')

    def __zhidaoSign(self, url: str, data: dict) -> tuple[str, dict]:
        """处理 URL 和 body 数据，返回带签名的 URL 和更新后的 body"""
        # 解析 URL
        scheme, netloc, path, query_string, fragment = urlsplit(url)

        # 解析查询参数
        query_params = dict(parse_qsl(query_string))

        # 如果 sessionNid 不在 data 中，生成一个随机的
        if "sessionNid" not in data:
            data["sessionNid"] = self.__generate_random_session_nid()

        # 生成签名
        input_string = self.__build_input_string(data)
        signature = self.__generate_signature(input_string)

        # 添加签名到查询参数
        query_params['sign'] = signature

        # 重新构建查询字符串
        new_query_string = urlencode(query_params)

        # 重新构建 URL
        signed_url = urlunsplit(
            (scheme, netloc, path, new_query_string, fragment))

        return signed_url, data

    def _baseTemplate(self, question, choices, referenceMaterials: list, answer_type: str) -> str:
        if len(referenceMaterials) == 0:
            reserenceMaterial = ""
        else:
            reserenceMaterial = "参考资料：\n".join(
                [f"```{material.get('name', '')}\n{material.get('content', '')}\n```" for material in referenceMaterials])

        aiBackground = f"假设你是一名学生，正在学习《{self.extra.get('courseName', '未知课程')}》。需要严格按照考试要求完成一道题目，否则无法及格。\n"
        theme = f"现在，你学习到了{self.extra.get('theme', '未知主题')}。\n" if "theme" in self.extra else ""
        knowledgePoint = f"本次考察知识点为{self.extra.get('knowledgePoint', '未知知识点')}。\n" if "knowledgePoint" in self.extra else ""

        answerRequirment = f"""本题为{answer_type}，请从选项中选择{'最合适的答案' if answer_type == '单选题' else '所有正确的答案'}，回答放到markdown代码块中，例如：

        ```answer
        [{{"id": 652308395, "content": "<p>仅涉及心、肺、肝、肾及脑相关疾病</p>"}}]
        ```
        答案必须为满足格式的json字符串(列表，单选也要是列表)，否则视为无效答案，不能得分。在这个markdown代码块（answer）外，你需要解释为什么你认为这个答案是正确的，并且标注出你选择这个答案的依据，这些依据必须有一定的权威性。（我提供给你的参考资料绝对权威可信）
        """
        questionContent = f"现在，请听题：\n\n{question}\n\n"
        choicesContent = f"选项如下：```choices\n{json.dumps(choices, ensure_ascii=False, indent=4)}\n```\n"
        return reserenceMaterial + aiBackground + theme + knowledgePoint + answerRequirment + questionContent + choicesContent

    def singleChoiceTemplate(self, question, choices, referenceMaterials: list = []) -> str:
        return self._baseTemplate(question, choices, referenceMaterials, "单选题")

    def multipleChoiceTemplate(self, question, choices, referenceMaterials: list = []) -> str:
        return self._baseTemplate(question, choices, referenceMaterials, "多选题")

    def judgementTemplate(self, question, choices, referenceMaterials: list = []) -> str:
        return self._baseTemplate(question, choices, referenceMaterials, "判断题")

    def generateAnswer(self, prompt: str, choices: list = None) -> list:
        tokens = self.encoder.encode(prompt)

        # 如果大于32ktoken，取后32ktoken
        if len(tokens) > 27.900 * 1000:
            tokens = tokens[-27.900 * 1000:]

            prompt = self.encoder.decode(tokens)
            logger.warning(
                f"Prompt is too long, truncated to {len(tokens)} tokens")
        if self.useZhidao:
            aicompletion = self.zhiDaoCompletion(prompt, max_retries=int(self.extra.get("ai_retries", 1)))
        else:
            aicompletion = self.openaiCompletion(prompt)

        answers = self.parseAnswer(aicompletion, choices)
        if not answers:
            raise ValueError(f"Answer block not found in completion: {aicompletion[:200]}")
        return answers

    @staticmethod
    def parseAnswer(text: str, choices: list = None) -> list:
        """
        ### 从 AI 回复中解析答案
        先找 markdown 代码块里的 JSON；不行再退化为“选项 id / 选项内容 / 选项字母”匹配，
        兼容模型不按格式输出的情况。
        """
        if not text:
            return None
        for pattern in (r"```answer\s*(.*?)\s*```", r"```json\s*(.*?)\s*```",
                        r"(\[\s*\{.*?\}\s*\])"):
            match = re.search(pattern, text, re.DOTALL)
            if not match:
                continue
            raw = match.group(1).strip()
            try:
                data = json.loads(raw)
            except Exception:
                try:
                    data = ast.literal_eval(raw)
                except Exception:
                    continue
            if isinstance(data, list) and data:
                ids = []
                for item in data:
                    if isinstance(item, dict) and "id" in item:
                        ids.append(item["id"])
                    elif isinstance(item, (int, str)):
                        ids.append(item)
                if ids:
                    return ids
        if not choices:
            return None
        plain = re.sub(r"<[^>]+>", "", text)
        id_hits = [c["id"] for c in choices if str(c["id"]) in plain]
        if len(id_hits) == 1:
            return id_hits
        content_hits = []
        for c in choices:
            content = re.sub(r"<[^>]+>", "", str(c.get("content", ""))).strip()
            if len(content) >= 2 and content in plain:
                content_hits.append(c["id"])
        if len(content_hits) == 1:
            return content_hits
        letters = re.findall(r"(?:答案|应选|选择|故选)[^A-Da-d]{0,10}([A-Da-d]{1,4})", plain)
        if letters:
            ids = []
            for ch in letters[0].upper():
                idx = ord(ch) - ord("A")
                if 0 <= idx < len(choices):
                    ids.append(choices[idx]["id"])
            if ids:
                return ids
        match = re.search(r"\b([A-D])\b", plain)
        if match:
            idx = ord(match.group(1)) - ord("A")
            if 0 <= idx < len(choices):
                return [choices[idx]["id"]]
        return None

class PptToTxt:
    def __init__(self, moonShotKey,baseUrl="https://api.moonshot.cn/v1", max_file_size_mb=100, max_cache_files=500, max_cache_size_gb=8, delete_immediately=False):
        self.__moonShotKey = moonShotKey 
        self.__session = requests.Session()
        self.__download_path = getRealPath("AiDownloadCache")
        self.__client = OpenAI(
            api_key=self.__moonShotKey,
            base_url="https://api.moonshot.cn/v1",
        )
        self.__max_file_size = max_file_size_mb * 1024 * 1024  # Convert to bytes
        self.__max_cache_files = max_cache_files
        self.__max_cache_size = max_cache_size_gb * \
            1024 * 1024 * 1024  # Convert to bytes
        self.__delete_immediately = delete_immediately
        self.__file_cache = {}
        self.__initialize_cache()

    def __initialize_cache(self):
        file_list = self.__client.files.list()
        for file in file_list.data:
            self.__file_cache[file.filename] = {
                'id': file.id,
                'size': file.bytes,
                'created_at': file.created_at
            }

    def parseTxt(self, url: str) -> str:
        try:
            local_path = self.__getFilePath(url)
            file_size = os.path.getsize(local_path)
            if file_size > self.__max_file_size:
                raise ValueError(
                    f"File size ({file_size} bytes) exceeds the maximum allowed size ({self.__max_file_size} bytes)")

            file_id = self.__uploadFile(local_path)
            text_content = self.__extractText(file_id)
            self.__manage_cache()
            return text_content
        except Exception as e:
            logger.error(f"Error processing file from URL {url}: {str(e)}")
            return ""

    def __getFilePath(self, url: str) -> str:
        parsed_url = urlparse(url)
        file_path = parsed_url.path.lstrip('/')
        local_path = os.path.join(self.__download_path, file_path)

        if os.path.exists(local_path):
            logger.info(f"File already exists: {local_path}")
            return local_path

        return self.__downloadFile(url)

    def __downloadFile(self, url: str) -> str:
        response = self.__session.get(url, stream=True)
        if response.status_code == 200:
            parsed_url = urlparse(url)
            file_path = parsed_url.path.lstrip('/')
            local_path = os.path.join(self.__download_path, file_path)

            os.makedirs(os.path.dirname(local_path), exist_ok=True)

            with open(local_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)

            logger.info(f"File downloaded: {local_path}")
            return local_path
        else:
            raise Exception(f"Failed to download file: {response.status_code}")

    def __uploadFile(self, filePath: str) -> str:
        filename = os.path.basename(filePath)
        file_size = os.path.getsize(filePath)

        if filename in self.__file_cache and self.__file_cache[filename]['size'] == file_size:
            logger.info(
                f"File {filename} already exists on the server. Using existing file.")
            return self.__file_cache[filename]['id']

        file_object = self.__client.files.create(
            file=Path(filePath), purpose="file-extract")
        self.__file_cache[filename] = {
            'id': file_object.id,
            'size': file_size,
            'created_at': datetime.now().timestamp()
        }
        return file_object.id

    def __extractText(self, file_id: str) -> str:
        try:
            file_content = self.__client.files.content(file_id=file_id).text

            try:
                json_content = json.loads(file_content)
                return json_content.get("content", file_content)
            except json.JSONDecodeError:
                return file_content
        finally:
            if self.__delete_immediately:
                self.__deleteFile(file_id)

    def __deleteFile(self, file_id: str):
        try:
            self.__client.files.delete(file_id=file_id)
            logger.info(
                f"File with ID {file_id} deleted from MoonShot remote server")
            # Remove from cache
            self.__file_cache = {
                k: v for k, v in self.__file_cache.items() if v['id'] != file_id}
        except Exception as e:
            logger.error(f"Error deleting file with ID {file_id}: {str(e)}")

    def __manage_cache(self):
        total_size = sum(file['size'] for file in self.__file_cache.values())
        total_files = len(self.__file_cache)

        while (total_files > self.__max_cache_files or total_size > self.__max_cache_size) and self.__file_cache:
            oldest_file = min(self.__file_cache.items(),
                              key=lambda x: x[1]['created_at'])
            self.__deleteFile(oldest_file[1]['id'])
            total_size -= oldest_file[1]['size']
            total_files -= 1