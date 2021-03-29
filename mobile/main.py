import os
import time
import platform
from datetime import datetime, timezone
import firebase_admin
from firebase_admin import credentials, firestore

app_name = {
    'airtel': 'com.myairtelapp',
    'jio': 'com.jio.myjio',
    'tatasky': 'com.ryzmedia.tatasky',
    'vi': 'com.mventus.selfcare.activity'
}

cur_dir = os.getcwd()

db = None
phones = []
ips = []

def initFirebase():
    global db
    cred = credentials.Certificate('../serviceAccountKey.json')
    firebase_admin.initialize_app(cred)
    db = firestore.client()
    print('Database Connected')

def getIPAddr():
    global db, phones, ips
    docs = db.collection('ip-debug').stream()
    phones = []
    ips = []
    for doc in docs:
        phones.append(doc.id)
        ips.append(doc.to_dict()['ip'])

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

    global ips

    if is_usb:
        # Change Port
        os.popen('adb tcpip 5555')

        device = os.popen("adb devices").read().split('\n', 1)[1].split("device")[0].strip()

        print('Waiting for connection ...')
        connect = os.popen('adb connect ' + device).read()
        print(connect)
    
    else:
        # TODO: Error handling
        for ip in range(len(ips)):
            print('Waiting for connection ...')
            connect = os.popen('adb connect ' + ips[ip]).read()
            print(connect)

def disconnect_device():
    os.popen('adb disconnect')

def extractAirtel():
    global app_name, cur_dir

    operator = 'airtel'

    os.system('adb shell monkey -p ' + app_name[operator] + ' -c android.intent.category.LAUNCHER 1')

    init_delay = 15

    # Wait while the app opens
    time.sleep(init_delay)

    screenshotNum = 0
    curTime = getTime()

    delay = 3
    count = 9

    os.system('adb shell input swipe 300 1200 300 750')
    
    for i in range(count):

        fileName = operator + '-1-' + getTime() + '.png'
        fullFileName = os.path.join(cur_dir, 'mobile', 'images', fileName)
        fullFileName = fullFileName.replace("\\", "/")

        screenshotCmd = 'adb exec-out screencap -p > ' + fullFileName
        os.system(screenshotCmd)

        time.sleep(delay)
    
    os.system('adb shell input swipe 300 1200 300 700')
    
    for i in range(count):

        fileName = operator + '-2-' + getTime() + '.png'
        fullFileName = os.path.join(cur_dir, 'mobile', 'images', fileName)
        fullFileName = fullFileName.replace("\\", "/")

        screenshotCmd = 'adb exec-out screencap -p > ' + fullFileName
        os.system(screenshotCmd)

        time.sleep(delay)

def extractJio():

    # Give permissions initially

    global app_name, cur_dir

    operator = 'jio'

    os.system('adb shell monkey -p ' + app_name[operator] + ' -c android.intent.category.LAUNCHER 1')

    init_delay = 15

    # Wait while the app opens
    time.sleep(init_delay)

    screenshotNum = 0
    curTime = getTime()

    delay = 3
    count = 9

    accel = 10
    
    for i in range(count):

        fileName = operator + '-1-' + getTime() + '.png'
        fullFileName = os.path.join(cur_dir, 'mobile', 'images', fileName)
        fullFileName = fullFileName.replace("\\", "/")

        screenshotCmd = 'adb exec-out screencap -p > ' + fullFileName
        os.system(screenshotCmd)

        x2 = 230

        os.system('adb shell input swipe 600 600 ' + str(x2) + ' 600')

initFirebase()
getIPAddr()

os.chdir(getPath())

connect_device(is_usb=False)
# extractAirtel()
# extractJio()
disconnect_device()