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
from difflib import SequenceMatcher
import datainspection as di
import pandas
import csv

LOADDATA= True
if LOADDATA:
    cdd = di.loadCleanServiceData()
    weblinks = di.websiteAndLlinks(cdd)
    pddf = di.loadQuotes()
    texts = di.loadTexts()



def similarityScore(s1, s2):
    return SequenceMatcher(None, s1, s2).ratio()

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

def chooselink(listoflinks, keywords, url = ""):
    #Bag of Words kinda method
    possiblelinks = []
    for link in listoflinks:
        count = 0 
        for word in keywords:
            if word in link:
                count += 1
        if count >= 2:
            possiblelinks.append(link)
    return possiblelinks

def chooseLink2(listoflinks, url, quoteDoc):
    linksandscores = []
    url = di.getFullUrl(url)
    for link in listoflinks:
        link = link.replace(url,"")
        score = similarityScore(link, quoteDoc)
        linksandscores.append((link,score)) 

    def sortTuple(tup):  
        tup.sort(key = lambda x: x[1], reverse = True)  
        return tup
    
    return sortTuple(linksandscores)

def linksAndScores(pddf, url):
    listoflinks = getLinks(url)
    c_data = pddf[pddf["url"] == url]
    quotedocs = list(set(c_data.quoteDoc))
    linksdict = {}
    for quotedoc in quotedocs:
        scorelist = chooseLink2(listoflinks, url, quotedoc)
        linksdict[quotedoc] = scorelist
    return linksdict
    

cols = ["url","source_url","text"]
path = r"C:\Users\luka5132\Documents\GitHub\NLPToS\data\\"


stopped = "https://www.visible.com/legal/terms-of-use"

def textFromLinks(linksdict, colnames = cols, startlink = None):
    linkneeded = False
    if startlink:
        linkneeded = True
    else:
        with open('texts.csv', 'w') as f:
            writer = csv.writer(f)
            writer.writerow(colnames)
            
    for link in linksdict:
        linkslist = linksdict[link]
        for sourcelink in linkslist:
            if linkneeded:
                print("Skipping: ",sourcelink)
                linkneeded = not startlink == sourcelink
            else:
                print("Processing: ",sourcelink)
                try:
                    downloaded = trafilatura.fetch_url(sourcelink)
                    text = trafilatura.extract(downloaded)
                    text = text.replace("\n", " ")
                except:
                    text = ''
                
                newrow = [link, sourcelink, text]
                try:
                    with open('texts.csv', 'a') as f:
                        writer = csv.writer(f)
                        writer.writerow(newrow)
                except:
                    pass
    return None
    
#URL = pickRandomFile(lodata)
#page = requests.get(URL)
#soup = BeautifulSoup(page.content, 'html.parser')
#html_page = urlopen(URL)

#downloaded = trafilatura.fetch_url(URL)
#text = trafilatura.extract(downloaded)
#text = text.replace("\n", " ")