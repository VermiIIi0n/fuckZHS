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

    def fuckCourse(self, course_id:str):
        """
        ### Fuck the whole course
        * `course_id`: `courseId`(Hike) or `recuitAndCourseId`(Zhidao)
        """
        if re.match(r".*[a-zA-Z].*", course_id): # determine if it's a courseId or a recruitAndCourseId
            self.fuckZhidaoCourse(course_id) # it's a recruitAndCourseId
        else: # it's a courseId
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

class ExamCtx:
    def __init__(self, fucker: Fucker, courseId: int, knowledgeId: int, examTestId: int, examPaperId: int, progress_view: bool = True, aiConfig: dict = {}, opExtra: dict = {}):
        self.fucker = fucker
        self.courseId = courseId
        self.examTestId = examTestId
        self.examPaperId = examPaperId
        self.knowledgeId = knowledgeId
        self.opExtra = opExtra
        self.aiConfig = aiConfig
        self.progress_view = progress_view

        self.answerCache = {}
        self.sheetContent = None
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

    def readAnswerCache(self, examTestId):
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

        return self.answerCache

    def writeAnswerCacheToDisk(self):
        answerpath = self.getAnswerpath(self.examTestId)
        with open(answerpath, "w", encoding="utf-8") as f:
            json.dump(self.answerCache, f, ensure_ascii=False, indent=4)

    def getAnswer(self, questionId: int, version: int = 1) -> dict | None:
        key = str(questionId) if version == 1 else f"{questionId}_{version}"
        result = self.answerCache.get(key)
        return result

    def setAnswer(self, questionId: int, version: int, answer_data: dict):
        self.answerCache[str(questionId) if version == 1 else f"{questionId}_{version}"] = {
            "version": version,
            "question": answer_data.get("question", ""),
            "answer": answer_data.get("answer", ""),
            "answer_content": answer_data.get("answer_content", ""),
            "questionDict": answer_data.get("questionDict", {})
        }
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
                         args=(10,)).start()
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
            self.sheetContent = ret["data"]["partSheetVos"][0]["questionSheetVos"]
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
        if len(answers) == 0:
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

        # 尝试从缓存中获取答案
        answer = self.getAnswer(questionId, version)
        if answer is not None:
            answer = answer.get("answer", "").split('#@#')

            # 随机睡眠3-5秒，模拟网络延迟
            time.sleep(randint(3, 5))
            return answer, "cached"

        # 答案不存在，获取题目内容，使用AI生成答案
        questionContent = questionDict["content"]

        # 选项，只保留有id和content的选项
        choices = [
            {"id": option["id"], "content": option["content"]}
            for option in questionDict["optionVos"]
            if "id" in option and "content" in option
        ]

        # 选项数量少于2个，答案就是选项内容
        if len(choices) < 2:
            answer = choices[0]["id"]
            return [answer]

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
            answer = op.generateAnswer(prompt)
            return answer, "AI generated"
        except Exception as e:
            # 随机生成答案
            if questionType == 1:
                answer = self.select_random_answers(choices, 1)
            elif questionType == 2:
                answer = self.select_random_answers(choices, 2)

            time.sleep(randint(3, 5))

        return answer, "random"

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

        # 打开考试
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
            answer, note = self.getQuestionAnswer(questionContentDict)

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

    def generateAnswer(self, prompt: str) -> list:
        tokens = self.encoder.encode(prompt)

        # 如果大于32ktoken，取后32ktoken
        if len(tokens) > 27.900 * 1000:
            tokens = tokens[-27.900 * 1000:]

            prompt = self.encoder.decode(tokens)
            logger.warning(
                f"Prompt is too long, truncated to {len(tokens)} tokens")
        if self.useZhidao:
            aicompletion = self.zhiDaoCompletion(prompt)
        else:
            aicompletion = self.openaiCompletion(prompt)

        # 寻找```answer \n ... \n```块
        answer_block = re.search(
            r"```answer\n(.*?)\n```", aicompletion, re.DOTALL)
        if answer_block is None:
            raise ValueError("Answer block not found in completion")

        # 解析答案
        answer_str = answer_block.group(1)
        try:
            # 首先尝试用 json.loads
            answer_list = json.loads(answer_str)
        except json.JSONDecodeError:
            try:
                # 如果 json.loads 失败，尝试用 ast.literal_eval
                answer_list = ast.literal_eval(answer_str)
            except (ValueError, SyntaxError):
                raise ValueError(f"Invalid answer format: {answer_str}")

        if not isinstance(answer_list, list):
            raise ValueError(
                f"Answer should be a list, got: {type(answer_list)}")

        answers = []
        # 验证答案格式
        for answer in answer_list:
            if not isinstance(answer, dict) or "id" not in answer or "content" not in answer:
                raise ValueError(f"Invalid answer format: {answer}")
            answers.append(answer["id"])

        return answers

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