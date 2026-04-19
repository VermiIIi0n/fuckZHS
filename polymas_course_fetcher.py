"""
Polymas 课程列表获取模块
适配新的 cloudapi.polymas.com API

修复内容：
1. 使用新的 Polymas API 端点
2. 支持新的认证机制（ai-poly, zhs-jt-cas cookies）
3. 正确获取课程列表数据
"""

import requests
import json


class PolymasCourseFetcher:
    """Polymas 平台的课程列表获取器"""

    def __init__(self, cookies=None, proxies=None):
        self.session = requests.Session()
        if cookies:
            self.session.cookies.update(cookies)
        self.proxies = proxies or {}

        # 标准请求头
        self.session.headers.update({
            "Accept": "application/json, text/plain, */*",
            "Accept-Encoding": "gzip, deflate, br",
            "Accept-Language": "zh-CN,zh;q=0.9",
            "Content-Type": "application/json",
            "Origin": "https://hike-teaching-center.polymas.com",
            "Referer": "https://hike-teaching-center.polymas.com/stu-hike/agent-course-hike/ai-course-center",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/100.0.4896.127 Safari/537.36"
        })

    def get_student_courses(self, page_no=1, page_size=20):
        """
        获取学生课程列表
        API: POST https://cloudapi.polymas.com/student-course/student/index/queryStudentCourse
        """
        url = "https://cloudapi.polymas.com/student-course/student/index/queryStudentCourse"

        data = {
            "pageNo": page_no,
            "pageSize": page_size
        }

        try:
            print("[DEBUG] 请求学生课程列表...")
            print("[DEBUG] URL: {}".format(url))
            print("[DEBUG] Data: {}".format(json.dumps(data)))

            r = self.session.post(url, json=data, proxies=self.proxies, timeout=10)
            result = r.json()

            print("[DEBUG] 响应 code: {}".format(result.get('code')))
            print("[DEBUG] 响应: {}".format(json.dumps(result, indent=2, ensure_ascii=False)[:1000]))

            if result.get('code') == 200:
                courses = result.get('data', {}).get('list', [])
                return courses
            elif result.get('code') == 401:
                print("[ERROR] 未授权，需要重新登录")
                return []
            else:
                print("[ERROR] API 返回错误: {}".format(result.get('msg')))
                return []

        except Exception as e:
            print("[ERROR] 获取学生课程失败: {}".format(e))
            return []

    def get_assistant_courses(self, page_no=1, page_size=20):
        """
        获取助教课程列表
        API: POST https://cloudapi.polymas.com/student-course/student/index/queryAssistantCourseList
        """
        url = "https://cloudapi.polymas.com/student-course/student/index/queryAssistantCourseList"

        data = {
            "pageNo": page_no,
            "pageSize": page_size
        }

        try:
            print("[DEBUG] 请求助教课程列表...")
            r = self.session.post(url, json=data, proxies=self.proxies, timeout=10)
            result = r.json()

            if result.get('code') == 200:
                courses = result.get('data', {}).get('list', [])
                return courses
            else:
                return []

        except Exception as e:
            print("[ERROR] 获取助教课程失败: {}".format(e))
            return []

    def get_identity(self):
        """
        获取用户身份信息
        API: GET https://cloudapi.polymas.com/oauth/token/getIdentity
        """
        url = "https://cloudapi.polymas.com/oauth/token/getIdentity"

        try:
            print("[DEBUG] 请求用户身份信息...")
            r = self.session.get(url, proxies=self.proxies, timeout=10)
            result = r.json()

            print("[DEBUG] 身份信息: {}".format(json.dumps(result, indent=2, ensure_ascii=False)))

            if result.get('code') == 200:
                return result.get('data', {})
            else:
                print("[ERROR] 获取身份失败: {}".format(result.get('msg')))
                return None

        except Exception as e:
            print("[ERROR] 获取身份信息失败: {}".format(e))
            return None

    def get_all_courses(self):
        """
        获取所有课程
        """
        print("\n" + "="*60)
        print("Polymas 课程列表获取")
        print("="*60)

        # 获取身份信息
        identity = self.get_identity()
        if identity:
            print("\n[OK] 用户身份信息:")
            print("  - 用户名: {}".format(identity.get('realName')))
            print("  - 学号: {}".format(identity.get('userCode')))
            print("  - 学校: {}".format(identity.get('schoolNid')))

        # 获取学生课程
        student_courses = self.get_student_courses()
        print("\n[INFO] 获取到 {} 个学生课程".format(len(student_courses)))

        # 获取助教课程
        assistant_courses = self.get_assistant_courses()
        print("[INFO] 获取到 {} 个助教课程".format(len(assistant_courses)))

        # 合并课程列表
        all_courses = student_courses + assistant_courses

        # 格式化输出
        print("\n" + "="*60)
        print("课程列表")
        print("="*60)

        for i, course in enumerate(all_courses, 1):
            # 安全获取课程信息
            course_name = course.get('courseName', 'Unknown')
            course_id = course.get('courseId', 'Unknown')
            class_id = course.get('classId', 'Unknown')
            course_type = course.get('courseType', 'Unknown')
            term_name = course.get('termName', 'Unknown')

            # 安全获取教师列表
            teachers = course.get('teachers') or []
            try:
                teacher_str = ', '.join([t.get('teacherName', '') for t in teachers])
            except:
                teacher_str = '暂无'

            print("\n{}. {}".format(i, course_name))
            print("   课程ID: {}".format(course_id))
            print("   课程类型: {}".format(course_type))
            print("   教师: {}".format(teacher_str))
            print("   学期: {}".format(term_name))
            print("   [用于刷课的ID: {}]".format(course_id))
            print("   [用于刷课的classID: {}]".format(class_id))

        print("\n" + "="*60)

        return all_courses


def fetch_and_save():
    """
    获取课程并保存到 execution.json
    """
    # 尝试读取 cookies
    cookies_path = "./cookies.json"
    import os

    if not os.path.exists(cookies_path):
        print("[ERROR] cookies.json 不存在，请先登录")
        print("\n请运行以下命令登录：")
        print("  python main.py --qrlogin")
        return None

    with open(cookies_path, 'r') as f:
        cookies = json.load(f)

    # 创建 fetcher
    fetcher = PolymasCourseFetcher(cookies=cookies)

    # 获取所有课程
    courses = fetcher.get_all_courses()

    if courses:
        # 转换为执行格式（增加 courseType 和 classId）
        exec_list = []
        for course in courses:
            exec_list.append({
                "name": course.get('courseName', '未知课程'),
                "id": str(course.get('courseId', '')),
                "courseType": course.get('courseType', ''),
                "classId": str(course.get('classId', ''))
            })

        # 保存到 execution.json
        with open('execution.json', 'w', encoding='utf-8') as f:
            json.dump(exec_list, f, indent=4, ensure_ascii=False)

        print("\n[OK] 课程列表已保存到 execution.json")
        print("共 {} 门课程".format(len(exec_list)))

        return exec_list
    else:
        print("\n[ERROR] 未能获取课程列表")
        print("\n可能的原因：")
        print("1. Cookies 中缺少必要的认证信息")
        print("2. Cookies 已过期")
        print("3. 需要从浏览器获取新的 cookies")

        print("\n[建议] 从浏览器复制 cookies:")
        print("1. 打开浏览器，登录 https://hike-teaching-center.polymas.com")
        print("2. 按 F12 打开开发者工具")
        print("3. 复制 Application > Cookies 中的 ai-poly 和 zhs-jt-cas")
        print("4. 更新 cookies.json")

        return None


if __name__ == "__main__":
    import sys

    print("="*60)
    print("Polymas 课程列表获取工具")
    print("="*60)

    courses = fetch_and_save()

    if not courses:
        sys.exit(1)
