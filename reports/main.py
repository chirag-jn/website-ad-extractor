import firebase_admin
from firebase_admin import credentials, firestore
import pandas as pd
import sys
import re
from datetime import timezone, datetime

db = None
phoneNums = None

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
        if type == 5:
            return 'phones-debug'
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
        if type == 5:
            return 'phones'

def getStream(type):
    print('Getting ' + getDbName(type))
    docs = db.collection(getDbName(type)).stream()
    return docs

def getPhoneNumDeets(phoneNum):
    global phoneNums
    if phoneNums is None:
        phoneNums = {}
        docs = getStream(5)
        for doc in docs:
            phoneNums[str(doc.id)] = doc.to_dict()
    try:
        if '+91' in str(phoneNum):
            phoneNum = int(str(phoneNum)[3:])
        return phoneNums[str(phoneNum)]
    except:
        print('Phone number mapping not found for ' + str(phoneNum))
        return {'region': '', 'mobile': phoneNum, 
                'plan': '', 'operator': ''}
        
def saveDf(dicts, type):
    df = pd.DataFrame(dicts)
    try:
        df.to_excel(getDbName(type) + '-' + getTime() + '.xlsx')
    except Exception as e:
        print('Error in saving xlsx, saving csv')
        print(e)
        df.to_csv(getDbName(type) + '-' + getTime() + '.csv')
    print(getDbName(type) + ' Saved')

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
            'provider': '',
            'plan': '',
            'region': '',
            'sender': dic['address'],
            'time': str(dic['time']),
            'body': str(dic['body']).strip()
        }

        phone_deets = getPhoneNumDeets(resp['phone'])
        resp['provider'] = phone_deets['operator']
        resp['plan'] = phone_deets['plan']
        resp['region'] = phone_deets['region']
        
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
            'provider': '',
            'plan': '',
            'region': '',
            'app': dic['packageName'],
            'ott': 'none',
            'time': str(dic['time']),
            'title': str(dic['title']).strip(),
            'has_image': False,
            'imageURL': '',
            'body': dic['text']
        }

        phone_deets = getPhoneNumDeets(resp['phone'])
        resp['provider'] = phone_deets['operator']
        resp['plan'] = phone_deets['plan']
        resp['region'] = phone_deets['region']

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
            'provider': '',
            'plan': '',
            'region': '',
            'app': dic['packageName'],
            'ott': 'none',
            'time': str(dic['time']),
            'title': str(dic['title']).strip(),
            'has_image': True,
            'imageURL': dic['downloadURL'],
            'body': dic['text']
        }

        phone_deets = getPhoneNumDeets(resp['phone'])
        resp['provider'] = phone_deets['operator']
        resp['plan'] = phone_deets['plan']
        resp['region'] = phone_deets['region']

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
            'provider': '',
            'plan': '',
            'region': '',
            'email': dic['receiver'],
            'sender': dic['sender'],
            'time': str(dic['time']),
            'subject': str(dic['subject']).strip(),
            'body': str(dic['body']).strip()
        }

        phone_deets = getPhoneNumDeets(resp['phone'])
        resp['provider'] = phone_deets['operator']
        resp['plan'] = phone_deets['plan']
        resp['region'] = phone_deets['region']

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