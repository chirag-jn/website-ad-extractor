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

def saveDf(dicts, type):
    df = pd.DataFrame(dicts)
    try:
        df.to_excel(getDbName(type) + '-' + getTime() + '.xlsx')
    except:
        print('Error in saving xlsx, saving csv')
        df.to_csv(getDbName(type) + '-' + getTime() + '.csv')
    print(getDbName(type) + ' Saved')

def getStream(type):
    print('Getting ' + getDbName(type))
    docs = db.collection(getDbName(type)).stream()
    return docs

def initFirebase():
    global db
    cred = credentials.Certificate('../serviceAccountKey.json')
    firebase_admin.initialize_app(cred)
    db = firestore.client()
    print('Database Connected')

def getSMS():
    type = 4
    docs = getStream(type)

    dicts = []
    for doc in docs:
        dicts.append(doc.to_dict())

    saveDf(dicts, type)

def getNotifications():
    type = 2
    docs = getStream(type)

    dicts = []
    for doc in docs:
        dicts.append(doc.to_dict())

    saveDf(dicts, type)

def getNotificationsImages():
    type = 3
    docs = getStream(type)

    dicts = []
    for doc in docs:
        dicts.append(doc.to_dict())

    saveDf(dicts, type)

def getEmails():
    type = 1
    docs = getStream(type)

    dicts = []
    for doc in docs:
        dic = doc.to_dict()
        resp = {
            'operator': dic['reason'],
            'phone': dic['mobile'],
            'email': dic['receiver'],
            'sender': dic['sender'],
            'time': dic['time'],
            'subject': dic['subject'],
            'body': dic['body']
        }
        dicts.append(resp)

    saveDf(dicts, type)

if __name__ == '__main__':
    initFirebase()
    # getSMS()
    # getNotificationsImages()
    getEmails()