import json
import time
from selenium import webdriver
from selenium.common.exceptions import (
    WebDriverException,
    TimeoutException,
    NoSuchWindowException,
    InvalidSessionIdException,
)
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager

LOGIN_URL = "https://passport.zhihuishu.com/login?service=https://onlineservice-api.zhihuishu.com/login/gologin"


class LoginError(Exception):
    """登录过程异常基类"""
    pass


class BrowserClosedError(LoginError):
    """浏览器被用户提前关闭"""
    pass


class LoginTimeoutError(LoginError):
    """登录等待超时"""
    pass


class ElementNotFoundError(LoginError):
    """关键元素定位失败"""
    pass


def login(username: str, password: str, save_path: str = "cookies.json", headless: bool = False, timeout: int = 300):
    """
    自动填充账号密码，点击登录，等待用户完成滑块验证后保存 Cookies。

    :param username: 智慧树账号
    :param password: 智慧树密码
    :param save_path: Cookies 保存路径，默认 cookies.json
    :param headless: 是否使用无头模式，默认 False（建议 False，滑块验证需要可见）
    :param timeout: 等待登录完成的最大秒数，默认 300 秒
    :raises LoginError: 各种登录失败场景
    """
    options = Options()
    if headless:
        options.add_argument("--headless")
        options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option('useAutomationExtension', False)
    options.page_load_strategy = 'normal'

    print("正在启动 Chrome 浏览器...")
    try:
        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=options)
    except Exception as e:
        raise LoginError(f"浏览器启动失败：{e}\n请确保已安装 Chrome 浏览器，或手动下载 ChromeDriver 并配置。")

    driver.set_page_load_timeout(30)  # 页面加载超时设为 30 秒
    wait = WebDriverWait(driver, 10)

    try:
        # 1. 打开登录页面
        try:
            driver.get(LOGIN_URL)
            print("登录页面加载中...")
        except TimeoutException:
            raise LoginError("登录页面加载超时，请检查网络或代理设置。")
        except WebDriverException as e:
            if "net::" in str(e):
                raise LoginError(f"网络连接失败：{e}")
            raise

        # 2. 定位并填写账号
        try:
            username_input = wait.until(EC.presence_of_element_located((By.ID, "lUsername")))
            username_input.clear()
            username_input.send_keys(username)
            print("已填写账号")
        except TimeoutException:
            raise ElementNotFoundError("账号输入框定位失败，页面元素可能已变更。")
        except WebDriverException as e:
            raise LoginError(f"填写账号时发生错误：{e}")

        # 3. 定位并填写密码
        try:
            password_input = wait.until(EC.presence_of_element_located((By.ID, "lPassword")))
            password_input.clear()
            password_input.send_keys(password)
            print("已填写密码")
        except TimeoutException:
            raise ElementNotFoundError("密码输入框定位失败，页面元素可能已变更。")
        except WebDriverException as e:
            raise LoginError(f"填写密码时发生错误：{e}")

        # 4. 定位并点击登录按钮
        try:
            login_btn = wait.until(EC.element_to_be_clickable((By.CLASS_NAME, "wall-sub-btn")))
            login_btn.click()
            print("已点击登录，请手动完成滑块验证...")
        except TimeoutException:
            raise ElementNotFoundError("登录按钮定位失败，页面元素可能已变更。")
        except WebDriverException as e:
            raise LoginError(f"点击登录按钮时发生错误：{e}")

        # 5. 等待用户完成登录（轮询检测 Cookie 和窗口状态）
        print(f"等待登录成功（最多 {timeout} 秒）...")
        start_time = time.time()
        login_success = False

        while time.time() - start_time < timeout:
            try:
                # 检测窗口是否被关闭
                if not driver.window_handles:
                    raise BrowserClosedError("浏览器窗口已被用户关闭，登录中断。")

                cookies = driver.get_cookies()
                if any(c['name'] == 'CASLOGC' for c in cookies):
                    login_success = True
                    print("检测到登录成功！")
                    break
            except (NoSuchWindowException, InvalidSessionIdException):
                raise BrowserClosedError("浏览器会话已失效（可能被用户关闭）。")
            except WebDriverException as e:
                # 其他 WebDriver 异常，可能是临时网络抖动，记录并继续尝试
                print(f"检测过程中发生临时错误：{e}，继续等待...")

            time.sleep(2)

        if not login_success:
            raise LoginTimeoutError(f"登录超时（{timeout}秒），未检测到 CASLOGC Cookie。")

        # 6. 保存 Cookies
        cookies_dict = {c['name']: c['value'] for c in driver.get_cookies()}
        with open(save_path, "w", encoding="utf-8") as f:
            json.dump(cookies_dict, f, indent=2, ensure_ascii=False)
        print(f"Cookies 已保存到 {save_path}，共 {len(cookies_dict)} 项。")

    except (BrowserClosedError, LoginTimeoutError, ElementNotFoundError) as e:
        print(f"登录失败：{e}")
        raise
    except Exception as e:
        print(f"发生未预期的错误：{e}")
        raise LoginError(f"未知错误：{e}")
    finally:
        # 确保浏览器被关闭，并处理可能已失效的 driver 对象
        try:
            driver.quit()
            print("浏览器已关闭。")
        except:
            pass  # 如果 quit 失败（例如浏览器已关闭），忽略


if __name__ == "__main__":
    try:
        user = input("请输入智慧树账号: ")
        pwd = input("请输入密码: ")
        login(user, pwd)
    except LoginError as e:
        print(f"\n[错误] {e}")
    except KeyboardInterrupt:
        print("\n用户中断操作。")
