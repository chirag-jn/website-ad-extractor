import time
from constants import operators, web_urls
from bs4 import BeautifulSoup
import requests
from urllib.parse import urljoin

def getAirtel():

    global web_urls, operators

    response = requests.get(web_urls[operators[0]]).text

    soup = BeautifulSoup(response, features='html.parser')

    img_container = soup.findAll('div', {'class': 'slide-container'})

    img_urls = []
    for i in img_container:
        img = i.find('img')
        img_urls.append(img['data-banner-src'])
    
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
