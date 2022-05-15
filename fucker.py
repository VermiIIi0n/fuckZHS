from zd_utils import Cipher, getEv, HOME_KEY, VIDEO_KEY, QA_KEY
from urllib.parse import unquote_plus as unquote
from requests.adapters import HTTPAdapter, Retry
from utils import progressBar, HMS
from random import randint, random
from threading import Thread
from base64 import b64encode
from getpass import getpass
from ObjDict import ObjDict
from logger import logger
from sign import sign
import requests
import urllib
import time
import json
import re
import os

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

class TimeLimitExceeded(Exception):
    pass

class Fucker:
    def __init__(self, cookies: dict = None,
                 headers: dict = None,
                 proxies: dict = None,
                 limit: int = 0,
                 speed: float = None,
                 end_thre: float = None):
        """
        ### Fucker Class
        * `cookies`: dict, optional, cookies to use for the session
        * `headers`: dict, optional, headers to use for the session
        * `proxies`: dict, optional, proxies to use for the session
        * `limit`: int, optional, time limit for each course, in minutes (default is 0), auto resets on fuck*Course methods call
        * `speed`: float, optional, video playback speed
        * `end_thre`: float, optional, threshold to stop the fucker, overloaded when there are questions left unanswered
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
                      status_forcelist=[ 500, 502, 503, 504])
        self.session = requests.Session()
        self.session.mount('http://', HTTPAdapter(max_retries=retry))
        self.session.mount('https://', HTTPAdapter(max_retries=retry))

        logger.debug(f'proxies: {self.proxies}')
        logger.debug(f'headers: {self.headers}')

        self.limit = abs(limit)                    # time limit for fucking, in minutes
        self.speed = speed and max(speed, 0.1)     # video play speed, Falsy values for default
        self.end_thre = min(end_thre or 0.91, 1.0) # video play end threshold, above this will be considered as finished
        self.prefix = "  |"                        # prefix for tree view
        self.context = ObjDict(default={})         # context for methods

    @property # cannot directly manipulate _cookies property, we need to parse uuid from cookies
    def cookies(self):
        return self._cookies

    @cookies.setter
    def cookies(self, cookies: dict|requests.cookies.RequestsCookieJar):
        self._cookies = cookies if isinstance(cookies, requests.cookies.RequestsCookieJar)\
                                else requests.utils.cookiejar_from_dict(cookies)
        logger.debug(f'received cookies: {self.cookies}')
        if cookies:
            try:
                self.uuid = json.loads(unquote(cookies["CASLOGC"]))["uuid"]
                self._cookies[f"exitRecod_{self.uuid}"] = "2"
            except Exception:
                raise ValueError("Cookies invalid")
        logger.debug(f"set cookies: {self._cookies}")

    def login(self, username: str=None, password: str=None, interactive: bool=True):
        """* `interactive`: whether to use interactive mode to login"""
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
            need_auth = self._apiQuery(check_url, {"uuid": user_info.uuid}).rt.needAuth
            if need_auth:
                raise Exception("account need auth, please login using browser to pass auth")
            self.session.get(login_page, params={"pwd": user_info.pwd}, proxies=self.proxies, timeout=10)
            self.cookies = self.session.cookies.copy()
            if not self.cookies:
                raise Exception("No cookies found")

            logger.info("Login successful")
        except Exception as e:
            logger.exception(e)
            raise Exception(f"Login failed: {e}")

    def fuckCourse(self, course_id:str, tree_view:bool=True):
        """
        ### Fuck the whole course
        * `course_id`: `courseId`(Hike) or `recuitAndCourseId`(Zhidao)
        * `tree_view`: whether to print the tree view of the progress
        """
        if re.match(r".*[a-zA-Z].*", course_id): # determine if it's a courseId or a recruitAndCourseId
            self.fuckZhidaoCourse(course_id, tree_view=tree_view) # it's a recruitAndCourseId
        else: # it's a courseId
            self.fuckHikeCourse(course_id, tree_view=tree_view)

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
    def getZhidaoContext(self, RAC_id:str, force:bool=False):
        """
        ### fetch context for zhidao course
        * `RAC_id`: `recruitAndCourseId`
        * `force`: force update
        """
        if RAC_id in self.context and not force:
            return self.context[RAC_id]
        self._checkCookies()
        logger.debug(f"Getting context for {RAC_id}")

        self._sessionReady()        # set cookies, headers, proxies
        self.session.headers.update({
            "Origin": "https://studyh5.zhihuishu.com",
            "Referer": "https://studyh5.zhihuishu.com/"
        })
        # urls
        login_url  = "https://studyservice-api.zhihuishu.com/login/gologin"
        videos_url = "https://studyservice-api.zhihuishu.com/gateway/t/v1/learning/videolist"
        course_url = "https://studyservice-api.zhihuishu.com/gateway/t/v1/learning/queryCourse"
        state_url  = "https://studyservice-api.zhihuishu.com/gateway/t/v1/learning/queryStuyInfo" # NOT MY TYPO
        read_url   = "https://studyservice-api.zhihuishu.com/gateway/t/v1/learning/queryStudyReadBefore"
        last_url   = "https://studyservice-api.zhihuishu.com/gateway/t/v1/learning/queryUserRecruitIdLastVideoId"

        # cross sites login
        params = {"fromurl": f"https://studyh5.zhihuishu.com/videoStudy.html#/studyVideo?recruitAndCourseId={RAC_id}"}
        self.session.get(login_url, params=params, proxies=self.proxies)

        data = {"recruitAndCourseId": RAC_id}
        # get course info, including recruitId, course name, etc
        course = self._zhidaoQuery(course_url, data).data
        recruit_id = course.recruitId

        # get chapters
        chapters = self._zhidaoQuery(videos_url, data).data
        chapters.default = [] # set default value for non exist attribute
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
        self._zhidaoQuery(read_url, data={"courseId": course_id, "recruitId": recruit_id})

        # get study info, including watchState, studyTotalTime
        data = {
            "lessonIds": lesson_ids,
            "lessonVideoIds": [video.id for video in videos.values() if video.id],
            "recruitId": recruit_id
        }
        states = self._zhidaoQuery(state_url, data=data).data
        states.default = ObjDict(default=False)   # set default value for non exist attribute
        for v in videos.values():
            state = states.lv[str(v.id)] or states.lesson[str(v.lessonId)]
            v.watchState, v.studyTotalTime = state.watchState, state.studyTotalTime

        # get most recently viewed video id, probably unneccessary, again, it's a POST request
        last_video = self._zhidaoQuery(last_url, data={"recruitId": recruit_id}).data.lastViewVideoId

        ctx = ObjDict({
            "course": course,
            "chapters": chapters,
            "videos": videos,
            "cookies": self.session.cookies.copy(),
            "headers": self.session.headers.copy(),
            "fucked_time": 0
        }, default={}) # store context for this course
        self.context[RAC_id] = ctx
        return ctx
        
    def fuckZhidaoCourse(self, RAC_id:str, tree_view:bool=True):
        """
        * `RAC_id`: `recruitAndCourseId`
        * `tree_view`: whether to print the tree progress view of the course
        """
        logger.info(f"Fucking Zhidao course {RAC_id}")
        tprint = print if tree_view else lambda *a, **k: None

        # load context
        ctx = self.getZhidaoContext(RAC_id)
        course = ctx.course
        chapters = ctx.chapters
        
        # start fucking
        begin_time = time.time() # real world time
        prefix = self.prefix # prefix for tree-like print
        w_lim = os.get_terminal_size().columns-1 # width limit for terminal output
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
                        tprint(prefix)
                        tprint(f"{prefix}##Fucking time limit exceeded: {e}\n")
                        return
                    except Exception as e:
                        logger.exception(e)
                        tprint(f"{prefix*3}##Failed: {e}"[:w_lim])
        tprint(prefix)
        tprint(f"{prefix}__Fucked course {course.courseInfo.name}, cost {time.time()-begin_time:.2f}s\n")
    
    def fuckZhidaoVideo(self, RAC_id, video_id):
        """
        * `RAC_id`: `recruitAndCourseId`
        * `video_id`: `videoId`
        """
        self._checkCookies()
        self._checkTimeLimit(RAC_id)

        # urls 
        note_url   = "https://studyservice-api.zhihuishu.com/gateway/t/v1/learning/prelearningNote"
        event_url  = "https://studyservice-api.zhihuishu.com/gateway/t/v1/popupAnswer/loadVideoPointerInfo"
        cache_url  = "https://studyservice-api.zhihuishu.com/gateway/t/v1/learning/saveCacheIntervalTime"
        record_url = "https://studyservice-api.zhihuishu.com/gateway/t/v1/learning/saveDatabaseIntervalTime"
        getQ_url   = "https://studyservice-api.zhihuishu.com/gateway/t/v1/popupAnswer/lessonPopupExam"
        subQ_url   = "https://studyservice-api.zhihuishu.com/gateway/t/v1/popupAnswer/saveLessonPopupExamSaveAnswer"

        ctx = self.getZhidaoContext(RAC_id)
        course_id = ctx.chapters.courseId
        recruit_id = ctx.course.recruitId
        video = ctx.videos[video_id]
        played_time = video.studyTotalTime
        watch_state = video.watchState
        if not video:
            raise ValueError(f"Video {video_id} not found")
        if watch_state == 1:
            logger.info(f"Video {video.name} already watched")
            return
        # get pre learning note
        data = {
            "ccCourseId": course_id,
            "chapterId": video.chapterId,
            "isApply": 1,
            "lessonId": video.lessonId, # this.lessonId
            "lessonVideoId": video.id, # this.smallLessonId
            "recruitId": recruit_id,
            "videoId": video.videoId 
        }
        token_id = self._zhidaoQuery(note_url, data=data).data.studiedLessonDto.id
        token_id = b64encode(str(token_id).encode()).decode()

        # get questions
        data = {
            "lessonId": video.lessonId,
            "lessonVideoId": video.id, 
            "recruitId": recruit_id, 
            "courseId": course_id
        }
        questions = self._zhidaoQuery(event_url, data=data).data.questionPoint
        questions = sorted(questions, key=lambda x: x.timeSec, reverse=True) if questions else None
        while questions and questions[-1].timeSec <= played_time:
            questions.pop() # remove questions that are already answered

        # compute end time and make sure to answer all questions
        end_time = video.videoSec * self.end_thre
        if questions:
            end_time = max(questions[0].timeSec, end_time) # compare last question time with end_time

        # emulating video playing
        watch_thread = Thread(target=self._watchVideo, args=(video.videoId,))
        watch_thread.start()

        # prepare vars
        speed = self.speed or 1.5  # default speed for Zhidao is 1.5
        start_at = played_time     # video time at start
        last_submit = played_time  # last pause time
        elapsed_time = 0    # real world time elapsed
        wp_interval = 2     # watch point update interval
        db_interval = 30    # database report interval
        cache_interval = 18 # cache report interval
        answer = None       # answer flag, do not modify
        report = False      # report flag, do not modify
        watch_point = "0,1" # watch point, do not modify
        pause = 0           # pause flag, do not modify

        ##### start main event loop, sort of...
        while played_time < end_time:
            time.sleep(1)
            ctx.fucked_time += 1 # for time limit check
            elapsed_time += 1
            played_time = min(played_time+speed, end_time) # update video time and make sure not exceeding end_time
            pause = pause or int(random() < 0.0025)*60 # randomly pause a minute, avoid detection
            report = report or pause == 60  # report on pause

            ### events
            ## get questions
            if questions and played_time >= questions[-1].timeSec:
                question = questions.pop()
                try:
                    question = self._zhidaoQuery(getQ_url, data={
                        "lessonId": video.lessonId, # this.lessonId
                        "lessonVideoId": video.id, # this.smallLessonId
                        "questionIds" : question.questionIds
                    }).data.lessonTestQuestionUseInterfaceDtos[0].testQuestion
                    answer = 2    # answer delay time
                    report = True # set report flag
                except Exception as e:
                    logger.error(f"can't get question detail:\n{e}")
            ## answer questions
            if answer is not None:
                if answer == 0:
                    answer = None # unset answer flag
                    self._zhidaoQuery(subQ_url, data={
                        "courseId": course_id, # this.courseId,
                        "recruitId": recruit_id, # this.recruitId
                        "testQuestionId": question.questionId, # this.pageList.testQuestion.questionId
                        "isCurrent": '1', # this.result ...it should be 'isCorrect'... in the name of lord, can somebody teach them eNgLIsH!!
                        "lessonId": video.lessonId, # this.lessonId
                        "lessonVideoId": video.id, # this.smallLessonId
                        "answer": self.answerZhidao(question), # this.answerStu.join(",")
                        "testType": 0 # always 0
                    })
                else:
                    pause = pause or 1 # emulate pause on pop quiz
                    answer -= 1
            ## update watch point
            if elapsed_time % wp_interval == 0:
                watch_point += f",{int((played_time-start_at)/5)+2}"
            ## report to database
            if elapsed_time % db_interval == 0 or played_time >= end_time or report:
                report = False # unset report flag
                # prepare for ev
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
                # prepare payload
                data = {
                    "watchPoint": watch_point,
                    "ev": getEv(raw_ev),
                    "learningTokenId": token_id
                }
                self._zhidaoQuery(record_url, data=data) # now submit to database
                last_submit = played_time # update last pause time
                watch_point = "0,1"       # reset watch point
            ## report to cache
            if elapsed_time % cache_interval == 0:
                # prepare ev
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
                data = {
                    "watchPoint": watch_point,
                    "ev": getEv(raw_ev),
                    "learningTokenId": token_id
                }
                self._zhidaoQuery(cache_url, data=data) # now submit to cache
                last_submit = played_time # update last pause time
                watch_point = "0,1"       # reset watch point
            ## on pause
            if pause:
                pause -= 1
                played_time = last_submit
            ### end events
            # print progress bar
            s, e = [60-pause, 60] if pause else [played_time, end_time]
            # have a glance of when quiz is answered
            action = "pause a minute" if pause else \
                    f"fucking {video.videoId}" if answer is None else "answering quiz"
            progressBar(s, e, prefix=action, suffix="done")
        ##### end main event loop
        time.sleep(random()+1) # old Joe needs more sleep

    def answerZhidao(self, q:dict):
        """you can override this function to answer questions"""
        q = ObjDict(q)
        a = [str(opt.id) for opt in q.questionOptions if opt.result=='1'] # choose correct answers
        return ','.join(a)

    def _zhidaoQuery(self, url:str, data:dict, encrypt:bool=True, ok_code:int=0,
               setTimeStamp:bool=True, method:str="POST"):
        """set ok_code to None for no check"""
        cipher = Cipher()
        if setTimeStamp:
            data["dateFormate"] = int(time.time())*1000 # somehow their timestamps are ending with 000
        logger.debug(f"{method} url: {url}\nraw_data: {json.dumps(data,indent=4,ensure_ascii=False)}")
        form ={"secretStr": cipher.encrypt(json.dumps(data))} if encrypt else data
        ret = self._apiQuery(url, data=form, method=method)
        if ok_code is not None and ret.code != ok_code:
            ret.default = None
            e = Exception(f"code: {ret.code} "+
                          f"msg: {ret.message or json.dumps(ret,indent=4,ensure_ascii=False)}")
            logger.error(e)
            raise e
        return ret

# end of zhidao methods
#############################################
# following are methods for hike API
    def getHikeContext(self, course_id:str, force:bool=False):
        if course_id in self.context and not force:
            return self.context[course_id]
        self._checkCookies()
        self._sessionReady() # set cookies, headers, proxies
        self.session.headers.update({
            "Origin": "https://hike.zhihuishu.com",
            "Referer": "https://hike.zhihuishu.com/"
        })
        url = "https://studyresources.zhihuishu.com/studyResources/stuResouce/queryResourceMenuTree"
        params = {"courseId": course_id}
        self._hikeQuery(url, params)
        root = self._hikeQuery(url, params).rt
        ctx = ObjDict({
            "root": root,
            "cookies": self.session.cookies.copy(),
            "headers": self.session.headers.copy(),
            "fucked_time": 0
        }, default={})
        self.context[course_id] = ctx
        return ctx
    
    def fuckHikeCourse(self, course_id:str, tree_view:bool=True):
        tprint = print if tree_view else lambda *a, **k: None
        begin_time = time.time()
        root = self.getHikeContext(course_id).root
        
        prefix = self.prefix
        logger.info(f"Fucking Hike course {course_id} (total root chapters: {len(root)})")
        tprint(f"Fucking course {course_id} (total root chapters: {len(root)})")
        for chapter in root:
            self._traverse(course_id, chapter, tree_view=tree_view)
        logger.info(f"Fucked course {course_id}, cost {time.time()-begin_time}s")
        tprint(prefix)
        tprint(f"{prefix}__Fucked course {course_id}, cost {time.time()-begin_time:.2f}s")

    def fuckHikeVideo(self, course_id, file_id, prev_time=0):
        self._checkCookies()
        self._checkTimeLimit(course_id)
        self._sessionReady() # set cookies, headers, proxies
        logger.info(f"Fucking Hike video {file_id} of course {course_id}")
        begin_time = time.time()
        ctx = self.getHikeContext(course_id)

        #urls
        url       = "https://hike-teaching.zhihuishu.com/stuStudy/saveStuStudyRecord"
        parse_url = "https://studyresources.zhihuishu.com/studyResources/stuResouce/stuViewFile"

        params = {
            "courseId": course_id,
            "fileId": file_id,
        }
        # get video info
        file_info = self._hikeQuery(parse_url, params)

        # emulating video playing
        watch_thread = Thread(target=self._watchVideo, args=(file_info.rt.dataId,))
        watch_thread.start()

        # getting ready to fuck
        params["uuid"] = self.uuid # add it now 'cause it shoudln't be in the params of parsing url
        total_time = int(file_info.rt.totalTime)
        start_date = int(time.time()*1000)
        watched_time = 0.0
        speed = self.speed or 1.25 # default speed for Hike is 1.25
        interval = 30              # interval between 2 progess reports
        end_time = total_time*self.end_thre
        # start main loop
        while (prev_time+watched_time) <= end_time:
            time.sleep(1)
            ctx.fucked_time += 1
            watched_time += speed
            watched_time = min(prev_time+watched_time, total_time) - prev_time
            # enter branch when video is finished or interval is reached
            if (prev_time+watched_time) >= end_time or \
                not (int(watched_time) % interval):
                params.update({
                    "studyTotalTime": int(watched_time),
                    "startWatchTime": int(prev_time),
                    "endWatchTime": int(prev_time+watched_time),
                    "startDate": start_date,
                    "endDate": int(time.time()*1000),
                })
                info = self._hikeQuery(url, params, sig=True, ok_code=200) # report progress
                logger.debug(f"json: status: {info.status}, msg: {info.message}, rt: {info.rt}")
                if info.rt is None:
                    raise Exception(
                        f"Failed to fuck video {file_id} of course {course_id}, \n"+
                        f"error: {info.status}, message: {info.message}, rt: {info.rt}")
                prev_time = info.rt
                watched_time = 0
            progressBar(watched_time+prev_time, end_time,
                        prefix=f"fucking {file_id}", suffix="of threshold")
        logger.info(f"Fucked video {file_id} of course {course_id}, cost {time.time()-begin_time:.2f}s")
        time.sleep(random()+1) # more human-like

    def fuckFile(self, course_id, file_id):
        params = {
            "courseId": course_id,
            "fileId": file_id,
            "_": int(time.time()*1000)
        }
        parse_url = "https://studyresources.zhihuishu.com/studyResources/stuResouce/stuViewFile"
        self.session.get(parse_url, params=params, proxies=self.proxies, timeout=10)
        time.sleep(random()*2+1) # more human-like

    def _traverse(self,course_id, node: ObjDict, depth=0, tree_view=True):
        depth += 1
        tprint = print if tree_view else lambda *a, **k: None
        w_lim = os.get_terminal_size().columns-1 # width limit for terminal output
        prefix = self.prefix * depth
        if node.childList: # if childList is not None, then it's a chapter
            chapter = node
            logger.debug(f"Fucking chapter {chapter.id}")
            tprint(prefix) # separate chapters
            tprint(f"{prefix}__Fucking chapter {chapter.name}"[:w_lim])
            for child in chapter.childList:
                self._traverse(course_id, child, depth=depth, tree_view=tree_view)
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

    def _hikeQuery(self, url:str, data:dict,sig:bool=False, ok_code:int=200,
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
# end of hike methods
#######################################
# shared private methods
    def _watchVideo(self, video_id): # it's probably unnecessary but let's keep it to fool those idiots
        headers = self.session.headers.copy()
        cookies = self.session.cookies.copy()
        # get video link
        parse_url = "https://newbase.zhihuishu.com/video/initVideo"
        r = self.session.get(parse_url, 
                            params={
                                "jsonpCallBack": "result",
                                "videoID": str(video_id),
                                "_": int(time.time()*1000)
                            },
                            cookies=cookies, headers=headers, proxies=self.proxies, timeout=10)
        r = re.match(r"^result\((.*)\)$",r.text).group(1)
        url = ObjDict(json.loads(r)).result.lines[0].lineUrl
        requests.get(url, headers=headers, cookies=cookies, proxies=self.proxies)

    def _apiQuery(self, url:str, data:dict, method:str="POST"):
        method = method.upper()
        logger.debug(f"{method} url: {url}\ndata: {json.dumps(data,indent=4,ensure_ascii=False)}\n"+
                     f"headers: {json.dumps(self.headers, indent=4)}\n"+
                     f"cookies: {self.session.cookies}\n"+
                     f"proxies: {json.dumps(self.session.proxies, indent=4)}")
        match method:
            case "POST":
                r = self.session.post(url, data=data, proxies=self.proxies, timeout=10)
            case "GET":
                r = self.session.get(url, params=data, proxies=self.proxies, timeout=10)
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
