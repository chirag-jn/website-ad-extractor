import os
import time
import platform
from datetime import datetime, timezone
import firebase_admin
from firebase_admin import credentials, firestore
from tqdm.auto import tqdm
from duplicateImages import DuplicateRemover

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

def unlock_device(ip_num):
    global ips, phones
    print('Unlocking Device ' + ips[ip_num] + ' with Num: ' + phones[ip_num])

    os.system('adb -s ' + ips[ip_num] + ' shell input keyevent 26')
    time.sleep(0.1)
    os.system('adb -s ' + ips[ip_num] + ' shell input swipe 300 1200 300 700')
    time.sleep(1)

def connect_device(ip_num = 0, is_usb = True):

    global ips, phones

    print('Connecting Device ' + ips[ip_num] + ' with Num: ' + phones[ip_num])

    if is_usb:
        # Change Port
        os.popen('adb tcpip 5555')

        device = os.popen("adb devices").read().split('\n', 1)[1].split("device")[0].strip()

        print('Waiting for connection ...')
        connect = os.popen('adb connect ' + device).read()
        print(connect)
    
    else:
        # TODO: Error handling
        # for ip in range(len(ips)):
        #     print('Waiting for connection ...')
        connect = os.popen('adb connect ' + ips[ip_num]).read()
        print(connect)

def disconnect_device():
    os.popen('adb disconnect')

def del_duplicates(operator):
    pathdr = os.path.join(cur_dir, 'images', operator)
    dr = DuplicateRemover(pathdr)
    dr.find_duplicates()

def extractAirtel(ip_num):
    global app_name, cur_dir, ips, phones

    operator = 'airtel'

    print('Extracting ' +  operator  + ' for ' + ips[ip_num] + ' with Num: ' + phones[ip_num])

    status = os.popen('adb -s ' + ips[ip_num] + ' shell monkey -p ' + app_name[operator] + ' -c android.intent.category.LAUNCHER 1').read()

    if 'No activities found to run, monkey aborted' in status:
        print(operator + ' app is not installed')
        return

    init_delay = 15

    # Wait while the app opens
    time.sleep(init_delay)

    screenshotNum = 0
    curTime = getTime()

    delay = 3
    count = 9

    for loc in range(3):
        os.system('adb -s ' + ips[ip_num] + ' shell input swipe 300 1200 300 750')
    
        for i in range(count):

            fileName = operator + '-' + str(loc)  + '-' + getTime() + '.png'
            fullFileName = os.path.join(cur_dir, 'images', operator, fileName)
            fullFileName = fullFileName.replace("\\", "/")

            screenshotCmd = 'adb -s ' + ips[ip_num] + ' exec-out screencap -p > ' + fullFileName
            os.system(screenshotCmd)

            time.sleep(delay)
    
    del_duplicates(operator)

def extractJio(ip_num):
    global app_name, cur_dir, ips, phones

    operator = 'jio'

    print('Extracting ' +  operator  + ' for ' + ips[ip_num] + ' with Num: ' + phones[ip_num])

    status = os.popen('adb -s ' + ips[ip_num] + ' shell monkey -p ' + app_name[operator] + ' -c android.intent.category.LAUNCHER 1').read()

    if 'No activities found to run, monkey aborted' in status:
        print(operator + ' app is not installed')
        return

    init_delay = 15

    # Wait while the app opens
    time.sleep(init_delay)

    screenshotNum = 0
    curTime = getTime()

    delay = 3
    count = 9

    for loc in range(3):
        os.system('adb -s ' + ips[ip_num] + ' shell input swipe 300 1200 300 1100')

        for i in range(count):

            fileName = operator  + '-' + str(loc)  + '-' + getTime() + '.png'
            fullFileName = os.path.join(cur_dir, 'images', operator, fileName)
            fullFileName = fullFileName.replace("\\", "/")

            screenshotCmd = 'adb -s ' + ips[ip_num] + ' exec-out screencap -p > ' + fullFileName
            os.system(screenshotCmd)

            x = 230

            os.system('adb -s ' + ips[ip_num] + ' shell input swipe 600 600 ' + str(x) + ' 600')

    del_duplicates(operator)

initFirebase()
getIPAddr()

os.chdir(getPath())

disconnect_device()

for i in range(len(ips)):

    connect_device(i, is_usb=False)
    unlock_device(i)
    extractAirtel(i)
    extractJio(i)
    disconnect_device()