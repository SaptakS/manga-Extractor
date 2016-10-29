import os
import urllib2
import requests
from BeautifulSoup import BeautifulSoup as bs
import re
from difflib import SequenceMatcher as sm
from PIL import Image
from StringIO import StringIO
from requests.exceptions import ConnectionError


PROXY = "http://<username>:<password>@<host>:<port>"
PROXY_DICT = {
				"http": PROXY,
				"https": PROXY,
				"ftp": PROXY
			 }

PROXY_SUPPORT = urllib2.ProxyHandler(PROXY_DICT)
OPENER = urllib2.build_opener(PROXY_SUPPORT)
urllib2.install_opener(OPENER)

def findNextURL(imageUrl):
    return imageUrl.parent["href"]

def saveImg(data):
    maxval = 0
    maxurl = ""
    imglinks = data.findAll("img")
    check_link = BASE_HOST.split("//")[1]
    if len(check_link.split('.')) > 2:
        check_link = check_link.split('.')[1] + "." + check_link.split('.')[2]
    for link in imglinks:
        if check_link in str(link['src']) and sm(None, str(link['src']), \
        	BASE_URL.replace("http", "")).ratio() > maxval:
            maxval = sm(None, str(link['src']), BASE_URL).ratio()
            maxl = link
            maxurl = link['src']
    if maxurl == '':
        for link in imglinks:
            if sm(None, str(link['src']), BASE_URL.replace("http", "")).ratio() > maxval:
                maxval = sm(None, str(link['src']), BASE_URL).ratio()
                maxl = link
                maxurl = link['src']

    if "http" not in str(maxurl):
        maxurl = BASE_HOST.split("//")[0] + maxurl

    try:
        image = requests.get(maxurl, proxies=PROXY_DICT)
        print "Images Saved Successfully"
    except:
        print "Error"
        exit(0)

    image_file = open(os.path.join(BASE_PATH, "%s.jpg") % IMAGE_TITLE, 'wb')
    try:
        Image.open(StringIO(image.content)).save(image_file, 'JPEG')
    except IOError, e:
        print "Couldnt Save:", e
    finally:
        image_file.close()

    return maxl


def linkData(url):
    try:
        r = requests.get(BASE_URL, proxies=PROXY_DICT)
        data = bs("".join(r.text))

        return data
    except urllib2.HTTPError, e:
        print e.fp.read()


BASE_PATH = raw_input("Enter Name of the Folder to save in:")
BASE_URL = raw_input("Enter the First Page URL:")
BASE_HOST = re.split(r"/", BASE_URL)[0] + "//" + re.split(r"/", BASE_URL)[2]
BASE_CHECK_LINK = BASE_URL
#print BASE_HOST
TOTAL_IMG = int(raw_input("Enter total images to download:"))
IMAGE_TITLE = 0

if not os.path.exists(BASE_PATH):
    os.makedirs(BASE_PATH)

IMAGEURL = saveImg(linkData(BASE_URL))

CTR = 0
while CTR < TOTAL_IMG - 1:
    IMAGE_TITLE = IMAGE_TITLE + 1
    NEXT_REL = findNextURL(IMAGEURL)
    if not "://" in NEXT_REL:
        if NEXT_REL.startswith("/"):
            BASE_URL = BASE_HOST + NEXT_REL
        else:
            BASE_URL = re.sub(r"\w+.html", NEXT_REL, BASE_URL)
    print "Next page is :", BASE_URL
    IMAGEURL = saveImg(linkData(BASE_URL))
    CTR = CTR + 1

print "Total Pages Downloaded: ", (CTR + 1)
