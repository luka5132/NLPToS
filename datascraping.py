# -*- coding: utf-8 -*-
"""
Created on Mon Feb  8 12:57:57 2021

@author: luka5132
"""

from bs4 import BeautifulSoup
from urllib.request import urlopen, Request
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

LOADDATA= False
if LOADDATA:
    cdd = di.loadCleanServiceData()
    weblinks = di.websiteAndLlinks(cdd)
    quotesdf = di.loadQuotes()
    textsdf = di.loadTexts()

def similarityScore(s1, s2):
    return SequenceMatcher(None, s1, s2).ratio()

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


        
    

cols = ["url","source_url","text"]
path = r"C:\Users\luka5132\Documents\GitHub\NLPToS\data\\"


stopped = "https://www.visible.com/legal/terms-of-use"

def textFromLinks(linksdict, csv_name = "texts", colnames = cols, startlink = None):
    linkneeded = False
    if startlink:
        linkneeded = True
    else:
        with open(csv_name + '.csv', 'w') as f:
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
                    with open(csv_name + '.csv', 'a') as f:
                        writer = csv.writer(f)
                        writer.writerow(newrow)
                except:
                    pass
    return None

def quotesInTexts(quotes, texts, simscore = 0.9, newdf = True):
    uniqueurls = list(set(texts.url))
    urlsnotquoted = []
    cols = quotes.columns
    url_i = cols.get_loc("url")
    source_i =cols.get_loc("source")
    quotetext_i = cols.get_loc("quoteText")
    keys = quotes.keys()
    
    if newdf:
        outputdf = pandas.DataFrame(columns = keys)
    
    
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
                        print("\n")
                        print("bestmatch: ",bestmatch[0],"\n")
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

    
def chooseLink3(listoflinks, url, quoteDoc):
    linksandscores = []
    for link in listoflinks:
        full_link = di.getFullUrl(url,link)
        try:
            bm = di.get_best_match(quoteDoc,full_link)
            score = bm[1]
        except:
            score = 0
            
        linksandscores.append((full_link, score))
    
    def sortTuple(tup):  
        tup.sort(key = lambda x: x[1], reverse = True)  
        return tup
    
    return sortTuple(linksandscores)


class ScrapeTexts(object):
    
    def __init__(self, quotesdf, outcols = cols, csv_name = "texts", sortlinks = chooseLink3):
        self.quotesdf = quotesdf
        self.sortlinks = sortlinks
        self.outputcsv = csv_name
        self.cols = outcols
        self.quotesn = 0
        self.textsn = 0
        self.all_url = None
        self.subdf = None
        self.url = None
        self.quotedoc = None
        self.listoflinks = None
        self.sortedlinks = None
    
        
    def createCSV(self):
        with open(self.outputcsv + '.csv', 'w') as f:
            writer = csv.writer(f)
            writer.writerow(self.cols)
            
    def appendCSV(self, applist):
        try:
            with open(self.outputcsv + '.csv', 'a') as f:
                writer = csv.writer(f)
                writer.writerow(applist)
        except:
            pass
        
    def getLinks(self, externalurl = '', keyword = False):
        if externalurl:
            url= externalurl
        else:
            url = self.url
        hdr = {'User-Agent': 'Mozilla/5.0'}
        req = Request(url,headers=hdr)
        html_page = urlopen(req)
        soup = BeautifulSoup(html_page, 'lxml')
        links = []
        
        if keyword:
            for link in soup.findAll('a', attrs={'href': re.compile(keyword)}):  
                links.append(link.get('href'))
        else:
            for link in soup.findAll('a'):  
                links.append(link.get('href'))
        
        remdups = list(set(links))
        newlinks = [link for link in remdups if len(links) >2]
        return newlinks
    
    def tryLinks(self, minscore = 0.6, simscore = 0.85, maxtry = 10, show = True):
        allquotesfound = False
        links_i = 0
        links_n = len(self.sortedlinks)
        
        cols = self.subdf.columns
        quotetext_i = cols.get_loc("quoteText")
        quotesource_i = cols.get_loc("source")
        quotesindex = self.subdf.index
        quotes_n = len(self.subdf)
        if links_i < links_n:
            score = self.sortedlinks[links_i][1]
        
        while links_i < links_n and links_i < maxtry \
        and not allquotesfound and score > minscore:
            print("linksindex: ",links_i)
            textfound = False
            link = self.sortedlinks[links_i][0]
            print("link: ",link,"\n")
            
            try:
                downloaded = trafilatura.fetch_url(link)
                text = trafilatura.extract(downloaded)
                text = text.replace("\n", " ")
                text = di.cleanText(text)
            except:
                text = ''
            
            if text:
                #print("text: \n\n",text)
                quotes_i = 0
                while quotes_i < quotes_n:
                    
                    if show:
                        print("processing: ",link,"quote nr: ",quotes_i)
                        print("total quotes processed: ",self.quotesn)
                        print("total quotes found: ",self.textsn,"\n")
                        self.quotesn += 1
                    
                    ind = quotesindex[quotes_i]
                    quote = self.subdf.iat[quotes_i,quotetext_i]
                    source = self.subdf.iat[quotes_i,quotesource_i]
                    if not isinstance(source, str):
                        bestmatch = di.get_best_match(quote,text)
                        score = bestmatch[1]
                        print("score: ",score)
                        if score > simscore:
                            self.quotesdf.loc[ind,"source"] = link
                            self.textsn +=1
                            textfound = True
                    
                    quotes_i += 1
            
            if textfound:
                newrow = [self.url, link, text]
                self.appendCSV(newrow)
            
            allquotesfound = all(self.subdf.source.notna())
            print("allquotesfound? ",allquotesfound)
            links_i +=1
            
        return None
    
    def linkByQuoteDoc(self):
        try:
            self.listoflinks = self.getLinks()
            self.sortedlinks = self.sortlinks(self.listoflinks, self.url, self.quotedoc)
            self.tryLinks()
        except:
            pass
        
        return None
        
    def scrapeFromDf(self, app = False):
        if not app:
            self.createCSV()
        
        self.all_url = list(set(self.quotesdf.url))
        for url in self.all_url:
            self.url = url
            self.subdf = self.quotesdf[self.quotesdf.url == url]
            
            quotedocs = list(set(self.subdf.quoteDoc)) +["legal"] #often used
            for quotedoc in quotedocs:
                self.quotedoc = quotedoc
                self.linkByQuoteDoc()
        
        return None


#URL = pickRandomFile(lodata)
#page = requests.get(URL)
#soup = BeautifulSoup(page.content, 'html.parser')
#html_page = urlopen(URL)

#downloaded = trafilatura.fetch_url(URL)
#text = trafilatura.extract(downloaded)
#text = text.replace("\n", " ")