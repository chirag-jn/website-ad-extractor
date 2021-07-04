import firebase_admin
from firebase_admin import credentials, firestore
import imaplib
import email
from email.header import decode_header
import os
import sys
import pandas as pd
from tqdm.auto import tqdm
import html2text
import re

db = None
_imap = None
htmlHandler = html2text.HTML2Text()
htmlHandler.ignore_links = True
htmlHandler.escape_snob = True

def initFirebase():
    global db
    cred = credentials.Certificate('../serviceAccountKey.json')
    firebase_admin.initialize_app(cred)
    db = firestore.client()
    print('Database Connected')

def getImap():
    global _imap
    if _imap is None:
        _imap = imaplib.IMAP4_SSL("imap.gmail.com")
        return _imap
    else:
        return _imap

def getDbName():
    try:
        _ = sys.argv[1]
        print('Selecting creds-debug DB')
        return 'creds-debug'
    except:
        print('Selecting creds DB')
        return 'creds'

def writeEmailsToFirebase():
    global db
    df = pd.read_csv('emails.csv')
    for i, row in tqdm(df.iterrows()):
        email_id = row['email']
        password = row['password']
        mobile = row['mobile']
        doc_ref = db.collection(getDbName()).document(str(email_id))
        doc_ref.set({
            'email': email_id,
            'password': password,
            'mobile': mobile
        })

def getEmailIdsFromFirebase():
    global db
    records = []
    for record in db.collection(getDbName()).stream():
        doc = record.to_dict()
        records.append(doc)
    return records

def clean(text):
    return "".join(c if c.isalnum() else "_" for c in text)

def checkIfMailContains(body):
    operators = ['airtel', 'vodafone', 'voda', 'jio', 'tatasky', 'idea', 'hotstar', 'netflix', 
                 'ullu', 'prime', 'video', 'zee5', 'voot', 'sony', 'sonyliv', 'eros', 'jiocinema', 'tvfplay']
    operator_keys = ['airtel', 'vi', 'vi', 'jio', 'tata', 'vi', 'hotstar', 'netflix', 
                     'ullu', 'primevideo', 'primevideo', 'zee5', 'voot', 'sony', 'sony', 'eros', 'jio', 'tvfplay']

    leftRe = '(^|[^a-z]+)'
    rightRe = '($|[^a-z]+)'

    for i in range(len(operators)):
        pattern = re.compile(leftRe + operators[i])
        if bool(pattern.search(body)):
            return operator_keys[i]
        
    pattern = re.compile(leftRe + 'vi' + rightRe)
    if bool(pattern.search(body)):
        return 'vi'
    
    return False

def getEmails(cred):

    global htmlHandler, db

    email_id = cred['email']
    password = cred['password']
    
    imap = getImap()
    
    try:
        imap.login(email_id, password)
    except Exception as e:
        print(email_id, end='\t')
        print(e)
        return
    
    status, messages = imap.select("INBOX")
    N = 1000
    num_messages = int(messages[0])
    N = num_messages

    for i in tqdm(range(num_messages,num_messages - N, -1)):

        res, msg = imap.fetch(str(i), "(RFC822)")
        for response in msg:
            if isinstance(response, tuple):

                mail_object = {
                    'id': '',
                    'time': '',
                    'subject': '',
                    'receiver': '',
                    'sender': '',
                    'body': '',
                    'reason': ''
                }

                msg = email.message_from_bytes(response[1])
                subject, encoding = decode_header(msg["Subject"])[0]
                date, encoding = decode_header(msg["Date"])[0]
                receiver, encoding = decode_header(msg["To"])[0]

                mail_object['subject'] = str(subject)
                mail_object['time'] = str(date)
                mail_object['receiver'] = str(receiver)

                if isinstance(subject, bytes):
                    try:
                        subject = subject.decode(encoding)
                    except:
                        subject = str(subject)
                From, encoding = decode_header(msg.get("From"))[0]
                if isinstance(From, bytes):
                    From = From.decode(encoding)
                
                mail_object['sender'] = str(From)

                if msg.is_multipart():
                    # iterate over email parts
                    for part in msg.walk():
                        # extract content type of email
                        content_type = part.get_content_type()
                        content_disposition = str(part.get("Content-Disposition"))
                        try:
                            body = part.get_payload(decode=True).decode()
                        except:
                            pass
                        if content_type == "text/plain" and "attachment" not in content_disposition:
                            mail_object['body'] += '\n' + str(htmlHandler.handle(body))

                        elif "attachment" in content_disposition:
                            continue
                            # attachment not needed
                            filename = part.get_filename()
                            if filename:
                                folder_name = clean(subject)
                                if not os.path.isdir(folder_name):
                                    # make a folder for this email (named after the subject)
                                    os.mkdir(folder_name)
                                filepath = os.path.join(folder_name, filename)
                                # download attachment and save it
                                open(filepath, "wb").write(part.get_payload(decode=True))
                else:
                    content_type = msg.get_content_type()
                    body = msg.get_payload(decode=True).decode()
                    if content_type == "text/plain":
                        mail_object['body'] += '\n' + str(htmlHandler.handle(body))

                if content_type == "text/html":
                    mail_object['body'] += '\n' + str(htmlHandler.handle(body))

                doesMailContain = checkIfMailContains(mail_object['body'].lower())
                if doesMailContain:
                    mail_object['reason'] = doesMailContain
                    mail_id = str(list(mail_object['time'].split(','))[1]) + ' --- ' + str(list(mail_object['receiver'].split('@'))[0])
                    mail_object['id'] = mail_id
                    doc_ref = db.collection('emails').document(mail_id)
                    doc_ref.set(mail_object)

    imap.close()
    imap.logout()


if __name__ == '__main__':
    initFirebase()
    creds = getEmailIdsFromFirebase()
    for cred in creds:
        print('Parsing Email:', cred['email'])
        getEmails(cred)