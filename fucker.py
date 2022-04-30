import urllib
from urllib.parse import unquote_plus as unquote
import json
import re
import time
import copy
from threading import Thread
import requests
from requests.adapters import HTTPAdapter, Retry
from logger import logger
import selenium
from selenium import webdriver
from selenium.webdriver.common.by import By
from utils import ObjDict
from sign import sign

class Fucker:
    def __init__(self, cookies: dict = None,
                 user_agent: str = None,
                 proxies: dict = None,
                 use_system_proxies: bool = True,
                 request_Session: requests.Session = None,
                 webdriver_opts: dict = None,
                 speed: float = None,
                 interval: int = None,
                 end_thre: float = None):
        logger.debug("created a Fucker")

        self._cookies = None
        self.uuid = None
        self.cookies = cookies or {}

        self.user_agent = user_agent or \
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/100.0.4896.127 Safari/537.36"
        logger.debug(f'user_agent: {self.user_agent}')

        self.proxies = proxies or (urllib.request.getproxies() if use_system_proxies else {})
        logger.debug(f'proxies: {self.proxies}')

        self.headers = {
            "Accept": "*/*",
            "User-Agent": self.user_agent,
            "Origin": "https://hike.zhihuishu.com",
            "Referer": "https://hike.zhihuishu.com/",
            "Accept-Encoding": "gzip, deflate, br",
            "Accept-Language": "en-GB,en;q=0.9"
        }
        retry = Retry(total=5,
                      backoff_factor=0.1,
                      raise_on_status=True,
                      status_forcelist=[ 500, 502, 503, 504])
        self.session = request_Session or requests.Session()
        self.session.mount('http://', HTTPAdapter(max_retries=retry))
        self.session.mount('https://', HTTPAdapter(max_retries=retry))
        self.webdriver_opts = webdriver_opts or {}
        logger.debug(f'webdriver_opts: {self.webdriver_opts}')

        self.speed = abs(speed or 1.25)             # video play speed
        self.end_thre = min(end_thre or 0.91, 1.0) # video play end threshold, above this will be considered as finished
        self.interval = max(interval or 10, 1)     # interval between two progress reports

    @property # cannot direct manipulate cookies, because we need uuid parsed from cookies
    def cookies(self):
        return self._cookies

    @cookies.setter
    def cookies(self, cookies: dict):
        self._cookies = requests.utils.cookiejar_from_dict(cookies)
        self.uuid = json.loads(unquote(cookies["CASLOGC"]))["uuid"] if cookies else None
        logger.debug(f"cookies: {self._cookies}")

    def login(self, username: str=None, password: str=None, webdriver_opts: dict=None):
        webdriver_opts = webdriver_opts or self.webdriver_opts
        while not username or not password:
            if not username:
                username = input("Username: ")
            else:
                print(f"Username: {username}")
            if not password:
                password = input("Password: ", hide=True)
        try:
            try:
                browser = webdriver.Chrome(**self.webdriver_opts)
            except Exception as e:
                logger.info(f"Failed to start Chrome: {e}")
                try:
                    browser = webdriver.Safari(**self.webdriver_opts)
                except Exception as e:
                    logger.info(f"Failed to start Safari: {e}")
                    try:
                        browser = webdriver.Firefox(**self.webdriver_opts)
                    except Exception as e:
                        logger.info(f"Failed to start Firefox: {e}")
                        logger.critical("Failed to start any browser, please install one of them and their webdriver")
                        return {}

            cookies_url = "https://passport.zhihuishu.com/login"
            browser.get(cookies_url)
            browser.find_element(by=By.ID, value="lUsername").send_keys(username)
            browser.find_element(by=By.ID, value="lPassword").send_keys(password)
            browser.find_element(by=By.XPATH,
                value="//span[@onclick=\"imgSlidePop(ImgSlideCheckModule.SignUpError3);\"]").click()
            time.sleep(5)
            cookies = browser.get_cookies()
            browser.close()

            if not cookies:
                logger.warning("No cookies found, please login first")
                return {}

            self._cookies.clear()
            cookies_list = {"SERVERID","CASTGC","CASLOGC","jt-cas"}
            for cookie in cookies:
                if cookie["name"] in cookies_list:
                    self._cookies[cookie["name"]] = cookie["value"]
            # now parse uuid from cookies
            self.uuid = json.loads(unquote(self._cookies["CASLOGC"]))["uuid"]
            self._cookies.update({"uuid": self.uuid,
                                f"exitRecod_{self.uuid}": "2"
                                })
            logger.debug(f"session cookies: {self.session.cookies}\ncookies: {self._cookies}")
            logger.info("Login successful")
            return self._cookies

        except selenium.common.exceptions.NoSuchWindowException as e:
            logger.error(
                f"Window is probably closed by user before getting cookies: {e}")
            return {}


    def fuckFile(self, course_id, file_id):
        params = {
            "courseId": course_id,
            "fileId": file_id,
            "_": int(time.time()*1000)
        }
        parse_url = "https://studyresources.zhihuishu.com/studyResources/stuResouce/stuViewFile"
        self.session.get(parse_url, params=params, timeout=10,
                        cookies=self._cookies, headers=self.headers, proxies=self.proxies)

    def _watchVideo(self, url: str): # it's probably unnecessary but let's keep it to fool those idiots
        headers = copy.copy(self.headers)
        cookies = copy.copy(self._cookies)
        requests.get(url, headers=headers, cookies=cookies, proxies=self.proxies)

    def fuckVideo(self, course_id, file_id, prev_time=0):
        if not self._cookies:
            logger.warning("No cookies found, please login first")
            return False

        logger.info(f"Fucking video {file_id} of course {course_id}")
        begin_time = time.time()
        url = "https://hike-teaching.zhihuishu.com/stuStudy/saveStuStudyRecord"

        params = {
            "courseId": course_id,
            "fileId": file_id,
            "_": int(time.time()*1000)
        }

        # get video info
        parse_url = "https://studyresources.zhihuishu.com/studyResources/stuResouce/stuViewFile"
        r = self.session.get(parse_url, params=params, timeout=10,
                            cookies=self._cookies, headers=self.headers, proxies=self.proxies)
        self._cookies.update(r.cookies)
        file_info = ObjDict(r.json())
        params["uuid"] = self.uuid # add it now 'cause it shoudln't be in parse_url

        # get video link
        parse_url = "https://newbase.zhihuishu.com/video/initVideo"
        data_id = file_info.rt.dataId
        r = self.session.get(parse_url, 
                            params={
                                "jsonpCallBack": "result",
                                "videoID": str(data_id),
                                "_": int(time.time()*1000)
                            },
                            cookies=self._cookies, headers=self.headers, proxies=self.proxies, timeout=10)
        r = re.match(r"^result\((.*)\)$",r.text).group(1)
        file_url = ObjDict(json.loads(r)).result.lines[0].lineUrl
        total_time = int(file_info.rt.totalTime)
        watched_time = 0.0

        watch_thread = Thread(target=self._watchVideo, args=(file_url,))
        watch_thread.start()
        start_date = int(time.time()*1000)

        while (prev_time+watched_time) <= total_time*self.end_thre:
            print(f"\rcurrent: {watched_time+prev_time:.1f}s/{total_time}s    "+
                  f"{(prev_time+watched_time)/total_time*100:.2f}%", end="")
            time.sleep(1)
            watched_time += self.speed
            if (prev_time+watched_time) >= total_time*self.end_thre or \
                not (int(watched_time) % self.interval):
                params.update({
                    "studyTotalTime": int(watched_time),
                    "startWatchTime": int(prev_time),
                    "endWatchTime": min(int(prev_time+watched_time), total_time),
                    "startDate": start_date,
                    "endDate": int(time.time()*1000),
                    "_": int(time.time()*1000)
                })
                for k,v in params.items():
                    params[k] = str(v)
                params["signature"] = sign(params)
                r = self.session.get(url, params=params, timeout=10,
                                cookies=self._cookies, proxies=self.proxies)
                self._cookies.update(r.cookies)
                info = ObjDict(r.json())
                logger.debug(f"json: status: {info.status}, msg: {info.message}, rt: {info.rt}")
                if info.status != 200 or info.rt is None:
                    raise Exception(
                        f"Failed to fuck video {file_id} of course {course_id}, \n"+
                        f"error: {info.status}, message: {info.message}, rt: {info.rt}")
                prev_time = info.rt
        logger.info(f"Fucked video {file_id} of course {course_id}, cost {time.time()-begin_time:.2f}s")

    def fuckCourse(self, course_id):
        if not self._cookies:
            logger.warning("No cookies found, please login first")
            return False

        begin_time = time.time()
        url = "https://studyresources.zhihuishu.com/studyResources/stuResouce/queryResourceMenuTree"
        params = {
            "courseId": course_id,
            "_": int(time.time()*1000)
        }
        r = self.session.get(url, params=params, cookies=self._cookies, proxies=self.proxies, timeout=10)
        chapters = ObjDict(r.json()).rt
        logger.info(f"Fucking course {course_id} (total chapters: {len(chapters)})")
        print(f"Fucking course {course_id} (total chapters: {len(chapters)})")
        for chapter in chapters:
            logger.debug(f"Fucking chapter {chapter.id}")
            print(f"    |\n\r    |__Fucking chapter {chapter.name}")
            for file in chapter.childList:
                file.studyTime = file.studyTime or 0 # sometimes it's None
                if file.studyTime >= file.totalTime*self.end_thre:
                    logger.debug(f"Skipped file {file.id}")
                    continue
                logger.debug(f"Fucking file {file.id}, data type: {file.dataType}")
                print(f"\r    |    |__Fucking {file.name}"[:81])
                try:
                    match file.dataType:
                        case 3:
                            self.fuckVideo(course_id, file.id, file.studyTime)
                        case _:
                            self.fuckFile(course_id, file.id)
                except Exception as e:
                    logger.error(f"Failed to fuck file {file.id} of course {course_id}")
                    logger.exception(e)
                    print(f"\r    |    ##Failed to fuck file {file.name}"[:81])
        logger.info(f"Fucked course {course_id}, cost {time.time()-begin_time}s")
        print(f"    |\n    |__Fucked course {course_id}, cost {time.time()-begin_time:.2f}s")
