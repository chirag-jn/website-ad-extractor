import os
import time
import platform
from datetime import datetime, timezone

app_name = {
    'airtel': 'com.myairtelapp',
    'jio': 'com.jio.myjio',
    'tatasky': 'com.ryzmedia.tatasky',
    'vi': 'com.mventus.selfcare.activity'
}

cur_dir = os.getcwd()

def getTime():
    return str(int(datetime.now(tz=timezone.utc).timestamp() * 1000))

def getPath():
    is_windows = any(platform.win32_ver())

    path = ''

    if is_windows:
        # TODO: Change Username to Runtime
        path = os.path.join('C:\\', 'Users', 'chira', 'AppData', 'Local', 'Android', 'Sdk', 'platform-tools')
    else:
        # TODO: Set Path
        path = os.path.join('/home', 'chirag', 'android-sdk-linux', 'platform-tools', 'adb')

    return path

def connect_device(is_usb):
    if not is_usb:
        # Change Port
        os.popen('adb tcpip 5555')

        device = os.popen("adb devices").read().split('\n', 1)[1].split("device")[0].strip()

        print('Waiting for connection ...')
        connect = os.popen('adb connect ' + device).read()
        print(connect)

def extractAirtel():
    global app_name, cur_dir

    operator = 'airtel'

    os.system('adb shell monkey -p ' + app_name[operator] + ' -c android.intent.category.LAUNCHER 1')

    # Wait while the app opens
    time.sleep(15)

    screenshotNum = 0
    curTime = getTime()

    os.system('adb shell input swipe 300 1200 300 800')
    
    os.system('adb shell input swipe 300 800 200 800')

    fileName = operator + '-' + getTime() + '.png'

    fullFileName = os.path.join(cur_dir, 'mobile', 'images', fileName)

    fullFileName = fullFileName.replace("\\", "/")

    screenshotCmd = 'adb exec-out screencap -p > ' + fullFileName

    os.system(screenshotCmd)


os.chdir(getPath())

connect_device(is_usb=True)
extractAirtel()