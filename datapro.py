# -*- coding: utf-8 -*-
"""
Created on Mon Feb  8 12:57:57 2021

@author: luka5132
"""

from bs4 import BeautifulSoup
from urllib.request import urlopen
import re
#import requests
#from boilerpy3 import extractors
#from selenium import webdriver
import trafilatura
import json
import glob
import os
import random
import string

script_dir = os.getcwd()
ptall = os.path.join(os.sep, script_dir,"Data/all.json")
ptservice = os.path.join(os.sep, script_dir,"Data/service")


TEST = False
LOAD = False


def stringIsLatin(s):
    return all([c in string.printable for c in s])

if LOAD:
    lodata = []
    errors = []
    for filename in glob.glob(os.path.join(ptservice, '*.json')):
        if stringIsLatin(filename):
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
    urlsplit = url.split(".")
    return urlsplit[1]


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
    """simple word counting method, definetly not best method, should look for
    more advanced"""
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

def pickRandomFile(lodata):
    n = len(lodata)
    return random.randint(0,n-1)
    
def inspectData(lodata):
    infdict = {}
    pagesrefferenced = 0
    totquotes = 0
    for rev in lodata:
        revdict = {}
        url = rev["urls"][0]
        webpages = set()
        nquotes = 0
        pd = rev["pointsData"]
        for p in pd:
            point = pd[p]
            totquotes += 1
            nquotes += 1
            try:
                webpages.add(point["quoteDoc"])
            except:
                print(point)
        pagesrefferenced += len(webpages)
        
        revdict["webpages"] = webpages
        revdict["nqt"] = nquotes
        infdict[url] = revdict
        
    infdict["totpages"] = pagesrefferenced
    infdict["totquotes"] = totquotes
    
    return infdict


if TEST:
    
    URL = pickRandomFile(lodata)
    #page = requests.get(URL)
    #soup = BeautifulSoup(page.content, 'html.parser')
    #html_page = urlopen(URL)

    downloaded = trafilatura.fetch_url(URL)
    text = trafilatura.extract(downloaded)
    text = text.replace("\n", " ")