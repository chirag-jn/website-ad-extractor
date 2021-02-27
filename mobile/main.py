import os
import time
import platform

app_name = {
    'airtel': 'com.myairtelapp',
    'jio': 'com.jio.myjio',
    'tatasky': 'com.ryzmedia.tatasky',
    'vi': 'com.mventus.selfcare.activity'
}

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
    global app_name

    operator = 'airtel'

    os.system('adb shell monkey -p ' + app_name[operator] + ' -c android.intent.category.LAUNCHER 1')

    # Wait while the app opens
    time.sleep(3)

    screenshotNum = 0
    curTime = getTime()

    os.system('adb shell input swipe 300 1200 300 800')
    
    os.system('adb shell input swipe 300 800 200 800')

    fileName = operator + '-' + getTime() + '.png'

    fullFileName = os.path.join('mobile', 'images', fileName)

    # adb exec-out screencap -p > screen.png


os.chdir(getPath())

connect_device(is_usb=True)
extractAirtel()