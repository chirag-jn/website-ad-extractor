import firebase_admin
from firebase_admin import credentials, firestore
import pandas as pd
import sys
from datetime import timezone, datetime

db = None

def getTime():
    return str(int(datetime.now(tz=timezone.utc).timestamp() * 1000))

def getDbName(type):
    try:
        _ = sys.argv[1]
        if type == 0:
            return 'ip-debug'
        if type == 1:
            return 'emails'
        if type == 2:
            return 'notifications-debug'
        if type == 3:
            return 'notifications-images-debug'
        if type == 4:
            return 'sms-debug'
    except:
        if type == 0:
            return 'ip'
        if type == 1:
            return 'emails'
        if type == 2:
            return 'notifications'
        if type == 3:
            return 'notifications-images'
        if type == 4:
            return 'sms'

def initFirebase():
    global db
    cred = credentials.Certificate('../serviceAccountKey.json')
    firebase_admin.initialize_app(cred)
    db = firestore.client()
    print('Database Connected')

def getSMS():
    print('Getting SMS')
    docs = db.collection('sms').stream()
    dicts = []
    for doc in docs:
        dicts.append(doc.to_dict())

    df = pd.DataFrame(dicts)
    df.to_csv('sms-' + getTime() + '.csv')
    print('SMS Saved')

def getNotifications():
    print('Getting Notifications')
    docs = db.collection('notifications').stream()
    dicts = []
    for doc in docs:
        dicts.append(doc.to_dict())

    df = pd.DataFrame(dicts)
    df.to_csv('notifications-' + getTime() + '.csv')
    print('Notifications Saved')

initFirebase()
getSMS()
getNotifications()