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
import time

LOADDATA= True
if LOADDATA:
    cdd = di.loadCleanServiceData()
    weblinks = di.websiteAndLlinks(cdd)
    quotesdf = di.loadQuotes()
    textsdf = di.loadTexts()

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

def quoteInText(quotes, texts, simscore = 0.9, newdf = True):
    uniqueurls = list(set(texts.url))
    
    urlsnotquoted = []
    
    if newdf:
        outputdf = pandas.DataFrame(columns = quotes.keys())
    
    
    thingsfound = 0
    nquotes = 0
    for url in uniqueurls:
        found = False
        try:
            subquotes = quotes[quotes["url"] == url]
            found = True
        except:
            urlsnotquoted.append(url)
        
        subtext = texts[texts["url"] == url]
        
        if found:
            subtexts = list(subtext.text)
            texts_surl = list(subtext.source_url)
            strquotes = list(subquotes["quoteText"])
            t_n = len(subtexts)
            
            
            for quote in strquotes:
                t_i = 0
                nquotes += 1
                quoteintext = False
                while t_i < t_n and not quoteintext:
                    text = subtexts[t_i]
                    print("processing quote: ",nquotes,"in text: ",t_i," total is: ",thingsfound)
                    try:
                        bestmatch = di.get_best_match(quote,text)
                        print("quote: ",quote)
                        print("\n\n")
                        print("bestmatch: ",bestmatch[0])
                        print("score: ",bestmatch[1])
                        if bestmatch[1] >= simscore:
                            
                            thingsfound +=1
                            source_url =  texts_surl[t_i]
                            
                            if newdf:
                                subquotes.loc[subquotes.quoteText == quote, 'source'] = source_url
                            else:
                                qindex = subquotes.index[subquotes.quoteText == quote][0]
                                quotes.loc[qindex, 'source'] = source_url
                            quoteintext = True
                    except:
                        pass
                    
                    t_i += 1
            
        if newdf:
            outputdf = outputdf.append(subquotes, ignore_index = True)
     
    print(thingsfound, nquotes)    
    if newdf:
        return outputdf
    else:
        return quotes
    
    

    
#URL = pickRandomFile(lodata)
#page = requests.get(URL)
#soup = BeautifulSoup(page.content, 'html.parser')
#html_page = urlopen(URL)

#downloaded = trafilatura.fetch_url(URL)
#text = trafilatura.extract(downloaded)
#text = text.replace("\n", " ")