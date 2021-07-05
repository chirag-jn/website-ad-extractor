import firebase_admin
from firebase_admin import credentials, firestore
import pandas as pd
from datetime import timezone, datetime

db = None

def getTime():
    return str(int(datetime.now(tz=timezone.utc).timestamp() * 1000))

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