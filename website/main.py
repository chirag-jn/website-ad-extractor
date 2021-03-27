import os
from datetime import timezone, datetime
from constants import operators, web_urls
from bs4 import BeautifulSoup
import requests
from urllib.parse import urljoin
import firebase_admin
from firebase_admin import credentials, firestore, storage

bucket = None

def getTime():
    return str(int(datetime.now(tz=timezone.utc).timestamp() * 1000))

def initFirebase():
    global bucket
    cred = credentials.Certificate('../serviceAccountKey.json')
    firebase_admin.initialize_app(cred, {
    'storageBucket': 'fuse-9747a.appspot.com'})
    bucket = storage.bucket()

def fileUpload(case, path):
    global bucket
    if not os.path.exists('images'):
        os.makedirs('images')

    r = requests.get(path, allow_redirects=True)
    fileTime = getTime()
    fileName = operators[case] + '-' + fileTime + '.' + path.split('.')[-1]
    fullFileName = os.path.join('images', fileName)
    open(fullFileName, 'wb+').write(r.content)

    blob = bucket.blob(fileName)
    blob.upload_from_filename(fullFileName)

    db = firestore.client()

    doc_ref = db.collection('images').document()
    doc_ref.create({
        'operator': operators[case], 
        'time': datetime.utcfromtimestamp(int(fileTime)//1000).strftime("%Y-%m-%d %H:%M:%S"),
        'url': blob.public_url
    })

def getAirtel():

    global web_urls, operators

    response = requests.get(web_urls[operators[0]]).text

    soup = BeautifulSoup(response, features='html.parser')

    img_container = soup.findAll('div', {'class': 'slide-container'})

    img_urls = []
    for i in img_container:
        img = i.find('img')
        url = img['data-banner-src'].split('?')[0]
        img_urls.append(url)
    
    return img_urls

def getJio():

    global web_urls, operators

    response = requests.get(web_urls[operators[2]]).text

    soup = BeautifulSoup(response, features='html.parser')
    div = soup.find('div', {'class': 'home_banner_slider'})

    a_container = div.findAll('a')

    img_urls = []
    for i in a_container:
        img = i.find('img', {'class': 'load_img_for_desktop'})
        img_urls.append(urljoin(web_urls[operators[2]], img['data-src-load']))
    
    return img_urls

def getVi():

    global web_urls, operators

    response = requests.get(web_urls[operators[1]])

    response.encoding = response.apparent_encoding

    response = str(response.text)

    soup = BeautifulSoup(response, features='html.parser')
    div = soup.find('div', {'class': 'vi_slider'})

    source_container = div.findAll('source',  {'media': '(min-width:768px)'})

    img_urls = []
    for i in source_container:
        img_urls.append(urljoin(web_urls[operators[1]], i['data-lazy-srcset']))
    
    return img_urls

def getTataSky():

    global web_urls, operators

    response = requests.get(web_urls[operators[3]])

    response.encoding = response.apparent_encoding

    response = str(response.text)

    soup = BeautifulSoup(response, features='html.parser')
    div = soup.find('div', {'class': 'offer-card-outer'})

    img_container = div.findAll('img')

    img_urls = []
    for i in img_container:
        img_urls.append(urljoin(web_urls[operators[3]], i['src']))
    
    return img_urls

def getUrls(case):
    if case == 0:
        return getAirtel()
    elif case == 1:
        return getVi()
    elif case == 2:
        return getJio()
    elif case == 3:
        return getTataSky()

def uploadImage():
    for case in range(len(operators)):
        urls = getUrls(case)
        for i in urls:
            fileUpload(case, i)

initFirebase()
uploadImage()