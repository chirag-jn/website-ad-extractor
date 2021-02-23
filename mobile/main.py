import os
import time
import platform

app_name = {
    'airtel': 'com.myairtelapp'
}

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

os.chdir(getPath())

is_local = True

if not is_local:
    # Change Port
    os.popen('adb tcpip 5555')

    device = os.popen("adb devices").read().split('\n', 1)[1].split("device")[0].strip()

    print('Waiting for connection ...')
    connect = os.popen('adb connect ' + device ).read()
    print(connect)

os.system('adb shell monkey -p ' + app_name['airtel'] + ' -c android.intent.category.LAUNCHER 1')

# Wait while the app opens
time.sleep(3)