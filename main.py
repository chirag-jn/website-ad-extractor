import time
from selenium.webdriver import Chrome
from selenium.webdriver.chrome.options import Options

opt = Options()
# opt.set_headless()

# assert opt.headless

browser = Chrome('drivers/chromedriver_win32/chromedriver.exe', options=opt)
browser.get('https://google.com')
time.sleep(5)
browser.quit()