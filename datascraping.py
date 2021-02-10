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


    
#URL = pickRandomFile(lodata)
#page = requests.get(URL)
#soup = BeautifulSoup(page.content, 'html.parser')
#html_page = urlopen(URL)

#downloaded = trafilatura.fetch_url(URL)
#text = trafilatura.extract(downloaded)
#text = text.replace("\n", " ")