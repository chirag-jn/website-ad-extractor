import firebase_admin
from firebase_admin import credentials, firestore
import imaplib
import email
from email.header import decode_header
import webbrowser
import os
import pandas as pd
from tqdm.auto import tqdm

db = None
_imap = None

def initFirebase():
    global db
    cred = credentials.Certificate('../serviceAccountKey.json')
    firebase_admin.initialize_app(cred)
    db = firestore.client()
    print('Database Connected')

def getEmailIds():
    df = pd.read_csv('emails.csv')
    return df

def getImap():
    global _imap
    if _imap is None:
        _imap = imaplib.IMAP4_SSL("imap.gmail.com")
        return _imap
    else:
        return _imap

def writeEmailsToFirebase():
    global db
    for i, row in tqdm(getEmailIds().iterrows()):
        email_id = row['email']
        password = row['password']
        mobile = row['mobile']
        doc_ref = db.collection('creds').document(str(email_id))
        doc_ref.set({
            'email': email_id,
            'password': password,
            'mobile': mobile
        })

def clean(text):
    return "".join(c if c.isalnum() else "_" for c in text)

def getEmails(email_id, password):
    
    imap = getImap()
    
    try:
        imap.login(email_id, password)
    except Exception as e:
        print(e)
        print(email_id)
    
    status, messages = imap.select("INBOX")
    N = 10
    num_messages = int(messages[0])
    print(num_messages)
    for i in range(num_messages, num_messages - N, -1):
        res, msg = imap.fetch(str(i), "(RFC822)")
        for response in msg:
            if isinstance(response, tuple):
                # parse a bytes email into a message object
                msg = email.message_from_bytes(response[1])
                # decode the email subject
                subject, encoding = decode_header(msg["Subject"])[0]
                if isinstance(subject, bytes):
                    # if it's a bytes, decode to str
                    subject = subject.decode(encoding)
                # decode email sender
                From, encoding = decode_header(msg.get("From"))[0]
                if isinstance(From, bytes):
                    From = From.decode(encoding)
                print("Subject:", subject)
                print("From:", From)
                # if the email message is multipart
                if msg.is_multipart():
                    # iterate over email parts
                    for part in msg.walk():
                        # extract content type of email
                        content_type = part.get_content_type()
                        content_disposition = str(part.get("Content-Disposition"))
                        try:
                            # get the email body
                            body = part.get_payload(decode=True).decode()
                        except:
                            pass
                        if content_type == "text/plain" and "attachment" not in content_disposition:
                            # print text/plain emails and skip attachments
                            print(body)
                        elif "attachment" in content_disposition:
                            # download attachment
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
                    # extract content type of email
                    content_type = msg.get_content_type()
                    # get the email body
                    body = msg.get_payload(decode=True).decode()
                    if content_type == "text/plain":
                        # print only text email parts
                        print(body)
                if content_type == "text/html":
                    # if it's HTML, create a new HTML file and open it in browser
                    folder_name = clean(subject)
                    if not os.path.isdir(folder_name):
                        # make a folder for this email (named after the subject)
                        os.mkdir(folder_name)
                    filename = "index.html"
                    filepath = os.path.join(folder_name, filename)
                    # write the file
                    open(filepath, "w").write(body)
                    # open in the default browser
                    webbrowser.open(filepath)
                print("="*100)
    # close the connection and logout
    imap.close()
    imap.logout()


if __name__ == '__main__':
    initFirebase()
    writeEmailsToFirebase()