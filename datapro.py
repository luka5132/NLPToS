# -*- coding: utf-8 -*-
"""
Created on Mon Feb  8 12:57:57 2021

@author: luka5132
"""

from bs4 import BeautifulSoup
from urllib.request import urlopen
import re
import requests
from boilerpy3 import extractors
from selenium import webdriver
import trafilatura
import json
import glob
import os
import random
import string


#options = webdriver.ChromeOptions()
#options.add_argument('--ignore-certificate-errors')
#options.add_argument('--incognito')
#options.add_argument('--headless')
#driver = webdriver.Chrome(r"C:\Users\luka5132\.wdm\drivers\chromedriver\win32\88.0.4324.96\chromedriver.exe", chrome_options=options) 


privacywords = ["privacy", "policy", "user", "statement", "policies", "data", 
                "regulations", "rules", "protection", "legislation"]
toswords = ["terms","service","agreement","user","contract","use","conditions","condition",
            "using","contract"]

script_dir = os.getcwd()
ptall = os.path.join(os.sep, script_dir,"Data/all.json")
ptservice = os.path.join(os.sep, script_dir,"Data/service")



LOAD = True
lodata = []
errors = []
if LOAD:
    for filename in glob.glob(os.path.join(ptservice, '*.json')):
        with open(filename,'r', encoding="utf8") as f:
            s = f.read()
            try:
                data = json.loads(s)
                lodata.append(data)
            except json.decoder.JSONDecodeError as e:
               errors.append((filename, e.msg))
        
    with open(ptall, "r", encoding="utf8") as f:
        s = f.read()
        try:
            alldata = json.loads(s)
        except json.decoder.JSONDecodeError as e:
            print(e.msg,e.pos, e.doc[e.pos-50:e.pos+50])



def getLinks(url, keyword = False):
    html_page = urlopen(url)
    soup = BeautifulSoup(html_page, 'lxml')
    links = []
    
    if keyword:
        for link in soup.findAll('a', attrs={'href': re.compile(keyword)}):  
            links.append(link.get('href'))
    else:
        for link in soup.findAll('a'):  
            links.append(link.get('href'))

    return links

def getWebsiteName(url):
    if url.startswith("https://"):
        url = url[8:]
    if url.startswith("www."):
        url = url[4:]
    dotpos = url.index(".")
    return url[:dotpos]


def getFilterSet(jsonfile):
    pointdsict = {}
    pointsData = jsonfile["pointsData"]
    url = jsonfile["urls"][0]
    websitename = getWebsiteName(url)
    for pd in pointsData:
        point = pointsData[pd]
        doc = point["quoteDoc"].lower()
        doc = doc.replace(websitename, "")
        doc = re.sub(r'[^\w\s]', '', doc) 
        wordset = set(doc.split())  
        pointdsict[doc] = wordset
    return pointdsict
        
        
def filterLinks(lolinks, pointsdict):
    linksdict = {}
    for doc in pointsdict:
        linkslist = []
        wordset = pointsdict[doc]
        for link in lolinks:
            lowerlink = link.lower()
            c = 0
            for word in wordset:
                if word in lowerlink:
                    c+=1
            if c > 0:
                linkslist.append((link, c))
        linkslist.sort(key=lambda tup: tup[1])
        linksdict[doc] = linkslist
    
    return linksdict

#privacy = getLinks("https://arstechnica.com", "privacy")
#terms = getLinks("https://arstechnica.com", "terms")

#print( privacy, terms )
#print( getLinks("https://arstechnica.com", "agreement") )

#URL = privacy[0]
#page = requests.get(URL)
#soup = BeautifulSoup(page.content, 'html.parser')
#html_page = urlopen(URL)

#downloaded = trafilatura.fetch_url(URL)
#text = trafilatura.extract(downloaded)
#text = text.replace("\n", " ")

def parse_html(html_path):
    with open(html_path, 'r') as fr:
        html_content = fr.read()
        soup = BeautifulSoup(html_content, 'html.parser')

        # Check that file is valid HTML
        if not soup.find():
            raise ValueError("File is not a valid HTML file")

        # Check the language of the file
        tag_meta_language = soup.head.find("meta", attrs={"http-equiv": "content-language"})
        if tag_meta_language:
            document_language = tag_meta_language["content"]
            if document_language and document_language not in ["en", "en-us", "en-US"]:
                raise ValueError("Language {} is not english".format(document_language))

        # Get text from the specified tags. Add more tags if necessary.
        TAGS = ['p']
        return ' '.join([remove_newline(tag.text) for tag in soup.findAll(TAGS)])
    
#extractor = extractors.ArticleExtractor()
#content = extractor.get_content_from_url(URL)

#text =[''.join(s.findAll(text=True))for s in soup.findAll('p')]
        
def chooselink(listoflinks, keywords):
    possiblelinks = []
    for link in listoflinks:
        count = 0 
        for word in keywords:
            if word in link:
                count += 1
        if count >= 2:
            possiblelinks.append(link)
    return possiblelinks