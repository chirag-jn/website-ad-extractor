import firebase_admin
from firebase_admin import credentials, firestore
import pandas as pd
import sys
import re
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
    except Exception as e:
        print('Error in saving xlsx, saving csv')
        print(e)
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

def checkIfBodyContainsVideo(body):

    body = str(body).lower()

    operators = ['hotstar', 'netflix', 
                 'ullu', 'prime', 'video', 'zee5', 'voot', 'sony', 'sonyliv', 'eros', 'jiocinema', 'tvfplay']
    operator_keys = ['hotstar', 'netflix', 
                     'ullu', 'primevideo', 'primevideo', 'zee5', 'voot', 'sony', 'sony', 'eros', 'jio', 'tvfplay']

    leftRe = '(^|[^a-z]+)'

    for i in range(len(operators)):
        pattern = re.compile(leftRe + operators[i])
        if bool(pattern.search(body)):
            return operator_keys[i]
    
    return False

def getSMS():
    type = 4
    docs = getStream(type)

    dicts = []
    for doc in docs:
        dic = doc.to_dict()
        resp = {
            'operator': dic['operator'],
            'ott': 'none',
            'phone': dic['phone'],
            'sender': dic['address'],
            'time': str(dic['time']),
            'body': str(dic['body']).strip()
        }
        
        bodyContainsVideo = checkIfBodyContainsVideo(resp['body'])
        if bodyContainsVideo:
            resp['ott'] = bodyContainsVideo

        dicts.append(resp)

    saveDf(dicts, type)

def getNotifications():
    type = 2
    docs = getStream(type)

    dicts = []
    for doc in docs:
        dic = doc.to_dict()
        resp = {
            'operator': dic['operator'],
            'phone': dic['phone'],
            'app': dic['packageName'],
            'ott': 'none',
            'time': str(dic['time']),
            'title': str(dic['title']).strip(),
            'has_image': False,
            'imageURL': '',
            'body': dic['text']
        }
        if 'displayText' in dic and not str(resp['body']).__contains__(dic['displayText']):
            resp['body'] = resp['body'] + '\n' + dic['displayText']
        if 'info' in dic and not str(resp['body']).__contains__(dic['info']):
            resp['body'] = resp['body'] + '\n' + dic['info']
        if 'summary' in dic and not str(resp['body']).__contains__(dic['summary']):
            resp['body'] = resp['body'] + '\n' + dic['summary']
        resp['body'] = resp['body'].strip()

        bodyContainsVideo = checkIfBodyContainsVideo(resp['body'])
        if bodyContainsVideo:
            resp['ott'] = bodyContainsVideo

        dicts.append(resp)

    print(getDbName(type) + ' Saved')

    type = 3
    docs = getStream(type)

    for doc in docs:
        dic = doc.to_dict()
        resp = {
            'operator': '',
            'phone': dic['phone'],
            'app': dic['packageName'],
            'ott': 'none',
            'time': str(dic['time']),
            'title': str(dic['title']).strip(),
            'has_image': True,
            'imageURL': dic['downloadURL'],
            'body': dic['text']
        }
        if 'tata' in resp['app']:
            resp['operator'] = 'tatasky'
        elif 'jio' in resp['app']:
            resp['operator'] = 'jio'
        elif 'airtel' in resp['app']:
            resp['operator'] = 'airtel'
        else:
            resp['operator'] = 'vi'
        if 'displayText' in dic and not str(resp['body']).__contains__(dic['displayText']):
            resp['body'] = resp['body'] + '\n' + dic['displayText']
        if 'info' in dic and not str(resp['body']).__contains__(dic['info']):
            resp['body'] = resp['body'] + '\n' + dic['info']
        if 'summary' in dic and not str(resp['body']).__contains__(dic['summary']):
            resp['body'] = resp['body'] + '\n' + dic['summary']
        resp['body'] = resp['body'].strip()

        bodyContainsVideo = checkIfBodyContainsVideo(resp['body'])
        if bodyContainsVideo:
            resp['ott'] = bodyContainsVideo

        dicts.append(resp)

    saveDf(dicts, 2)

def getEmails():
    type = 1
    docs = getStream(type)

    dicts = []
    for doc in docs:
        dic = doc.to_dict()
        resp = {
            'operator': dic['reason'],
            'ott': 'none',
            'phone': dic['mobile'],
            'email': dic['receiver'],
            'sender': dic['sender'],
            'time': str(dic['time']),
            'subject': str(dic['subject']).strip(),
            'body': str(dic['body']).strip()
        }

        bodyContainsVideo = checkIfBodyContainsVideo(resp['body'])
        if bodyContainsVideo:
            resp['ott'] = bodyContainsVideo

        dicts.append(resp)

    saveDf(dicts, type)

if __name__ == '__main__':
    initFirebase()
    getSMS()
    getNotifications()
    getEmails()