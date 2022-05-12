from zd_utils import Cipher, getEv, HOME_KEY, VIDEO_KEY, QA_KEY
from urllib.parse import unquote_plus as unquote
from requests.adapters import HTTPAdapter, Retry
from random import randint, random
from utils import progressBar, HMS
from collections import deque
from threading import Thread
from base64 import b64encode
from getpass import getpass
from ObjDict import ObjDict
from logger import logger
from lxml import html
from sign import sign
import requests
import urllib
import time
import json
import re
import os

class TimeLimitExceeded(Exception):
    pass

class InvalidCookies(ValueError):
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
        logger.debug(f"created a Fucker {id(self)}")

        self.uuid = None # actually it's not a uuid, but a random string
        self.cookies = cookies or {}
        self.proxies = proxies or urllib.request.getproxies() # explicitly use system proxy
        self.headers = headers or {
            "Accept": "*/*",
            "sec-ch-ua": "\" Not A;Brand\";v=\"99\", \"Chromium\";v=\"101\", \"Google Chrome\";v=\"101\"",
            "sec-ch-ua-mobile": "?0",
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/100.0.4896.127 Safari/537.36",
            "sec-ch-ua-platform": "macOS",
            "Origin": "https://hike.zhihuishu.com",
            "Referer": "https://hike.zhihuishu.com/",
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

        self.limit = abs(limit*60)                 # time limit for fucking
        self.total_studied_time = 0                # in seconds, fucking will stop when it reaches the limit
        self.speed = speed and max(speed, 0.1)     # video play speed, Falsy values for default
        self.end_thre = min(end_thre or 0.91, 1.0) # video play end threshold, above this will be considered as finished
        self.prefix = "    |"                      # prefix for tree view

    @property # cannot directly manipulate _cookies property, we need to parse uuid from cookies
    def cookies(self):
        return self._cookies

    @cookies.setter
    def cookies(self, cookies: dict|requests.cookies.RequestsCookieJar):
        self._cookies = cookies if isinstance(cookies, requests.cookies.RequestsCookieJar)\
                                else requests.utils.cookiejar_from_dict(cookies)
        if cookies:
            try:
                self.uuid = json.loads(unquote(cookies["CASLOGC"]))["uuid"]
                self._cookies[f"exitRecod_{self.uuid}"] = "2"
            except Exception:
                raise InvalidCookies()
        logger.debug(f"cookies: {self._cookies}")

    def login(self, username: str=None, password: str=None):
        while not username or not password:
            if not username:
                username = input("Username: ")
            else:
                print(f"Username: {username}")
            if not password:
                password = getpass("Password: ")
        # urls
        login_page = "https://passport.zhihuishu.com/login?service=https://onlineservice.zhihuishu.com/login/gologin"
        self._sessionReady() # set cookies, headers, proxies
        self.session.headers.update({
            "Origin": "https://passport.zhihuishu.com",
            "Referer": login_page
        })
        try:
            r = self.session.get(login_page, proxies=self.proxies, timeout=10)
            tree = html.fromstring(r.text)
            lt = tree.xpath("//input[@name=\"lt\"]")[0].attrib["value"]
            data = {
                "lt": lt,
                "execution": "e1s1",
                "_eventId": "submit",
                "username": username,
                "password": password,
                "clCode": "",
                "clPassword": "",
                "tlCode": "",
                "tlPassword": "",
                "remember": "on"
            }
            self.session.post(login_page,data=data, proxies=self.proxies, timeout=10)
            self.cookies = self.session.cookies.copy()
            if not self.cookies:
                raise Exception("No cookies found")

            logger.debug(f"session cookies: {self.session.cookies}\ncookies: {self.cookies}")
            logger.info("Login successful")
            print("Login successful")
        except InvalidCookies as e:
            logger.error(f"Invalid cookies")
            print("Invalid cookies, login failed")
        except Exception as e:
            logger.error(f"Login failed: {e}")
            print(f"Login failed: {e}")

    def fuckCourse(self, course_id:str):
        if re.match(r".*[a-zA-Z].*", course_id): # determine if it's a course id or a recruitAndCourseId
            self.fuckZhidaoCourse(course_id) # it's a recruitAndCourseId
        else: 
            self.fuckHikeCourse(course_id)

    def fuckVideo(self, course_id, video_id:str): # same as above
        if re.match(r".*[a-zA-Z].*", course_id):
            self.fuckHikeVideo(course_id, video_id)
        else:
            print("Fucking a single video is not supported when course id is a recruitAndCourseId\n"+
                  "and where the hell did you find this video id?")

#############################################
# for some fucking reasons
# there are 2 sets of completely different API for hike.zhihuishu.com and studyservice-api.zhihuishu.com
# so we need to use different methods for different API
#############################################
# following are methods for studyservice-api.zhihuishu.com API
    def fuckZhidaoCourse(self, RAC_id:str):
        """
        :param RAC_id: recruitAndCourseId
        :param video_ids: list of video ids
        """
        if not self._cookies:
            logger.warning("No cookies found, please login first")
        logger.info(f"Fucking Zhidao course {RAC_id}")

        self.total_studied_time = 0 # reset total studied time
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

        data = {"recruitAndCourseId": RAC_id}
        # login
        params = {"fromurl": f"https://studyh5.zhihuishu.com/videoStudy.html#/studyVideo?recruitAndCourseId={RAC_id}"}
        self.session.get(login_url, params=params, proxies=self.proxies)

        # get course info, including schoolId, recruitId, course name, etc
        course = self._apiQuery(course_url, data).data
        school_id = course.schoolId
        recruit_id = course.recruitId
        logger.info(f"course: {course.courseInfo.name}")

        # get videos list
        chapters = self._apiQuery(videos_url, data).data
        chapters.default = [] # set default value for non exist attribute
        logger.debug(json.dumps(chapters, indent=4))
        course_id = chapters.courseId
        lessons = []
        videos = []
        for chapter in chapters.videoChapterDtos:
            for l in chapter.videoLessons:
                lessons.append(l)
                for v in l.videoSmallLessons: 
                    videos.append(v)
        logger.info(f"{len(lessons)} lessons, {len(videos)} videos")
        if not lessons:
            print("No videos found, please check the course id")
            return
        print(f"Fucking course {course.courseInfo.name} "+
              f"(total root chapters: {len(chapters.videoChapterDtos)})")

        # get read before, maybe unneccessary. But hey, it's a POST request
        self._apiQuery(read_url, data={
            "courseId": course_id,
            "recruitId": recruit_id,
        })

        # get study info, including watchState, studyTotalTime
        data = {
            "lessonIds": [lesson.id for lesson in lessons],
            "lessonVideoIds": [video.id for video in videos],
            "recruitId": recruit_id
        }
        r = self._apiQuery(state_url, data=data).data
        r.default = {}        # set default value for non exist attribute
        r.lesson.update(r.lv) # join lesson and video info
        states = r.lesson

        # get most recently viewed video id, probably unneccessary, again, it's a POST request
        last_video = self._apiQuery(last_url, data={
            "recruitId": recruit_id
        }).data.lastViewVideoId
        
        # start fucking
        begin_time = time.time() # real world time
        prefix = self.prefix
        w_lim = os.get_terminal_size().columns-1 # width limit for terminal output
        for chapter in chapters.videoChapterDtos:
            print(prefix) # separator
            print(f"{prefix}__Fucking chapter {chapter.name}"[:w_lim])
            for lesson in chapter.videoLessons:
                print(f"{prefix*2}__Fucking lesson {lesson.name}"[:w_lim])
                if "videoId" in lesson: # no sublessons, only one video
                    lesson.lessonId = lesson.id
                    lesson.id = 0
                for video in lesson.videoSmallLessons or [lesson]:
                    print(f"{prefix*3}__Fucking video {video.name}"[:w_lim])
                    try:
                        state = states[str(video.id)]
                        # prepare ctx
                        ctx = ObjDict({
                            "course_id": course_id,
                            "recruit_id": recruit_id,
                            "chapter_id": chapter.id
                        })
                        self._fuckZhidaoVideo(video, state, ctx)
                    except TimeLimitExceeded as e:
                        logger.info(f"Learning time limit exceeded: {e}")
                        print("Learning time limit exceeded\n")
                        return
                    except Exception as e:
                        logger.exception(e)
                        print(f"{prefix*3}##Failed: {e}")
        print(f"{prefix}\n{prefix}__Fucked course {course.courseInfo.name}, cost {time.time()-begin_time:.2f}s\n")
    
    def _fuckZhidaoVideo(self, video:ObjDict, state:ObjDict, ctx:ObjDict):
        """
        :param video: video info
        :param ctx: context info, including course id, chapter id, recruit id, 
        """
        if self.limit and self.total_studied_time >= self.limit:
            print(f"{self.prefix*3}##Fucked enough, stop fucking")
            raise TimeLimitExceeded()

        # urls 
        note_url   = "https://studyservice-api.zhihuishu.com/gateway/t/v1/learning/prelearningNote"
        event_url  = "https://studyservice-api.zhihuishu.com/gateway/t/v1/popupAnswer/loadVideoPointerInfo"
        cache_url  = "https://studyservice-api.zhihuishu.com/gateway/t/v1/learning/saveCacheIntervalTime"
        record_url = "https://studyservice-api.zhihuishu.com/gateway/t/v1/learning/saveDatabaseIntervalTime"
        getQ_url   = "https://studyservice-api.zhihuishu.com/gateway/t/v1/popupAnswer/lessonPopupExam"
        subQ_url   = "https://studyservice-api.zhihuishu.com/gateway/t/v1/popupAnswer/saveLessonPopupExamSaveAnswer"

        played_time = state.studyTotalTime
        watch_state = state.watchState
        if watch_state == 1:
            logger.info(f"Video {video.name} already watched")
            return
        # get pre learning note
        data = {
            "ccCourseId": ctx.course_id,
            "chapterId": ctx.chapter_id,
            "isApply": 1,
            "lessonId": video.lessonId,
            "lessonVideoId": video.id,
            "recruitId": ctx.recruit_id,
            "videoId": video.videoId
        }
        token_id = self._apiQuery(note_url, data=data).data.studiedLessonDto.id
        token_id = b64encode(str(token_id).encode()).decode()

        # get questions
        data = {
            "lessonId": video.lessonId,
            "lessonVideoId": video.id, 
            "recruitId": ctx.recruit_id, 
            "courseId": ctx.course_id
        }
        questions = self._apiQuery(event_url, data=data).data.questionPoint
        questions = deque(sorted(questions, key=lambda x: x.timeSec)) if questions else None
        while questions and questions[0].timeSec <= played_time:
            questions.popleft() # remove questions that are already answered

        # compute end time and make sure to answer all questions
        end_time = video.videoSec * self.end_thre
        if questions:
            end_time = max(questions[-1].timeSec, end_time)

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

        ##### start main event loop, sort of...
        while played_time < end_time:
            time.sleep(1)
            self.total_studied_time += 1
            elapsed_time += 1
            played_time += speed

            ### events
            ## get questions
            if questions and played_time >= questions[0].timeSec:
                question = questions.popleft()
                try:
                    question = self._apiQuery(getQ_url, data={
                        "lessonId": video.lessonId,
                        "lessonVideoId": video.id,
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
                    report = True # set report flag
                    self._apiQuery(subQ_url, data={
                        "courseId": ctx.course_id,
                        "recruitId": ctx.recruit_id,
                        "testQuestionId": question.questionId,
                        "isCurrent": '1', # it should be 'isCorrect'...
                        "lessonId": video.lessonId,
                        "lessonVideoId": video.id,
                        "answer": self.answerZhidao(question),
                        "testType": 0
                    })
                else:
                    played_time -= speed # emulate pause on pop quiz
                    answer -= 1
            ## update watch point
            if elapsed_time % wp_interval == 0:
                watch_point += f",{int((played_time-start_at)/5)+2}"
            ## report to database
            if elapsed_time % db_interval == 0 or played_time >= end_time or report:
                report = False # unset report flag
                # prepare for ev
                raw_ev = [
                    ctx.recruit_id,
                    video.lessonId,
                    video.id,
                    video.videoId,
                    ctx.chapter_id,
                    '0',
                    int(played_time-last_submit),
                    int(played_time),
                    HMS(seconds=min(video.videoSec, # more realistic
                                    int(played_time+randint(29,31)))) 
                ]
                # prepare payload
                data = {
                    "watchPoint": watch_point,
                    "ev": getEv(raw_ev),
                    "learningTokenId": token_id
                }
                self._apiQuery(record_url, data=data) # now submit to database
                last_submit = played_time # update last pause time
                watch_point = "0,1"       # reset watch point
            ## report to cache
            if elapsed_time % cache_interval == 0:
                # prepare ev
                #!! NOTICE: content is different from database
                raw_ev = [
                    ctx.recruit_id,
                    ctx.chapter_id,
                    ctx.course_id,
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
                self._apiQuery(cache_url, data=data) # now submit to cache
                last_submit = played_time # update last pause time
                watch_point = "0,1"       # reset watch point
            ### end events

            progressBar(played_time, end_time, length=80, prefix=f"watching {video.name}", suffix="of threshold")
        ##### end main event loop
        time.sleep(random()+1)

    def answerZhidao(self, q:dict):
        """there is a sample of question object in README.md"""
        q = ObjDict(q)
        a = [str(opt.id) for opt in q.questionOptions if opt.result=='1']
        return ','.join(a)

    def _apiQuery(self, url:str, data:dict, encrypt:bool=True, ok_code:int=0,
               setTimeStamp:bool=True, method:str="POST"):
        """set ok_code to None for no check"""
        method = method.upper()
        cipher = Cipher()
        if setTimeStamp:
            data["dateFormate"] = int(time.time())*1000 # somehow their timestamps are ending with 000
        logger.debug(f"{method} url: {url}\ndata: {json.dumps(data, indent=4)}\n"+
                     f"headers: {json.dumps(self.headers, indent=4)}\n"+
                     f"cookies: {self.session.cookies}\n"+
                     f"proxies: {json.dumps(self.session.proxies, indent=4)}")
        form ={"secretStr": cipher.encrypt(json.dumps(data)) if encrypt else json.dumps(data)}
        match method:
            case "POST":
                r = self.session.post(url, data=form, proxies=self.proxies, timeout=10)
            case "GET":
                r = self.session.get(url, params=form, proxies=self.proxies, timeout=10)
            case _:
                e = ValueError(f"Unsupport method: {method}")
                logger.error(e)
                raise e
        ret = ObjDict(r.json())
        if ok_code is not None and ret.code != ok_code:
            e = Exception(ret.message)
            logger.error(e)
            raise e
        return ret


#############################################
# following are methods for hike API
    def fuckFile(self, course_id, file_id):
        params = {
            "courseId": course_id,
            "fileId": file_id,
            "_": int(time.time()*1000)
        }
        parse_url = "https://studyresources.zhihuishu.com/studyResources/stuResouce/stuViewFile"
        self.session.get(parse_url, params=params, proxies=self.proxies, timeout=10)
        time.sleep(random()*2+1) # more human-like

    def fuckHikeVideo(self, course_id, file_id, prev_time=0):
        if not self._cookies:
            logger.warning("No cookies found, please login first")
            return
        if self.limit and self.total_studied_time >= self.limit:
                logger.info(f"Studied time limit reached, video {file_id} skipped")
                return

        logger.info(f"Fucking Hike video {file_id} of course {course_id}")
        begin_time = time.time()
        self._sessionReady()        # set cookies, headers, proxies

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
        # start main loop
        while (prev_time+watched_time) <= total_time*self.end_thre:
            time.sleep(1)
            self.total_studied_time += 1
            watched_time += speed
            # enter branch when video is finished or interval is reached
            if (prev_time+watched_time) >= total_time*self.end_thre or \
                not (int(watched_time) % interval):
                params.update({
                    "studyTotalTime": int(watched_time),
                    "startWatchTime": int(prev_time),
                    "endWatchTime": min(int(prev_time+watched_time), total_time),
                    "startDate": start_date,
                    "endDate": int(time.time()*1000),
                })
                info = self._hikeQuery(url, params, sign=True, ok_code=200) # report progress
                logger.debug(f"json: status: {info.status}, msg: {info.message}, rt: {info.rt}")
                if info.rt is None:
                    raise Exception(
                        f"Failed to fuck video {file_id} of course {course_id}, \n"+
                        f"error: {info.status}, message: {info.message}, rt: {info.rt}")
                prev_time = info.rt
            progressBar(watched_time+prev_time, total_time*self.end_thre,
                        prefix=f"watching {file_id}", suffix="of threshold")
        logger.info(f"Fucked video {file_id} of course {course_id}, cost {time.time()-begin_time:.2f}s")
        time.sleep(random()+1) # more human-like
    
    def fuckHikeCourse(self, course_id:str):
        if not self._cookies:
            logger.warning("No cookies found, please login first")
            return
        self._sessionReady()        # set cookies, headers, proxies

        begin_time = time.time()
        self.total_studied_time = 0
        url = "https://studyresources.zhihuishu.com/studyResources/stuResouce/queryResourceMenuTree"
        params = {"courseId": course_id}
        self._hikeQuery(url, params)
        root = self._hikeQuery(url, params).rt
        logger.info(f"Fucking Hike course {course_id} (total root chapters: {len(root)})")

        print(f"Fucking course {course_id} (total root chapters: {len(root)})")
        for chapter in root:
            self._traverse(course_id, chapter)
        logger.info(f"Fucked course {course_id}, cost {time.time()-begin_time}s")

        prefix = self.prefix
        print(f"{prefix}\n{prefix}__Fucked course {course_id}, cost {time.time()-begin_time:.2f}s")

    def _traverse(self,course_id, node: ObjDict, depth=0):
        depth += 1
        w_lim = os.get_terminal_size().columns-1 # width limit for terminal output
        prefix = self.prefix * depth
        if node.childList: # if childList is not None, then it's a chapter
            chapter = node
            logger.debug(f"Fucking chapter {chapter.id}")
            print(prefix) # separate chapters
            print(f"{prefix}__Fucking chapter {chapter.name}"[:w_lim])
            for child in chapter.childList:
                self._traverse(course_id, child, depth=depth)
        else: # if childList is None, then it's a file
            file = node
            file.studyTime = file.studyTime or 0 # sometimes it's None
            logger.debug(f"Fucking file {file.id}, data type: {file.dataType}")
            print(f"{prefix}__Fucking {file.name}"[:w_lim])

            if file.studyTime >= file.totalTime*self.end_thre:
                logger.debug(f"Skipped file {file.id}")
                return

            try:
                match file.dataType:
                    case 3:
                        self.fuckHikeVideo(course_id, file.id, file.studyTime)
                    case None:
                        print(f"{prefix}##Unsupported file type, may be a quiz"[:w_lim])
                    case _:
                        self.fuckFile(course_id, file.id)
            except TimeLimitExceeded as e:
                logger.info(f"Time limit exceeded, video {file.id} skipped")
                print(f"{prefix}##Time limit exceeded, video skipped")
            except Exception as e:
                logger.error(f"Failed to fuck file {file.id} of course {course_id}")
                logger.exception(e)
                print(f"{prefix}##Failed: {e}"[:w_lim])

    def _hikeQuery(self, url:str, data:dict,sig:bool=False, ok_code:int=200,
                   setTimeStamp:bool=True, method:str="GET"):
        """set ok_code to None for no check"""
        method = method.upper()
        if setTimeStamp:
            data["_"] = int(time.time()*1000) # miliseconds
        if sig:
            for k,v in data.items():
                data[k] = str(v)
            data["signature"] = sign(data)
        logger.debug(f"{method} url: {url}\ndata: {json.dumps(data, indent=4)}\n"+
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
        if ok_code is not None and int(ret.status) != ok_code:
            e = Exception(f"{ret.status} {ret.msg}")
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

    def _sessionReady(self):
        self.session.cookies = self._cookies.copy()
        self.session.headers = self.headers.copy()
        self.session.proxies = self.proxies.copy()


