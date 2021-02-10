# -*- coding: utf-8 -*-
"""
Created on Wed Feb 10 20:12:30 2021

@author: luka5132
"""
import json
import glob
import os
import random
import string
import re

script_dir = os.getcwd()
ptall = os.path.join(os.sep, script_dir,"Data/all.json")
ptservice = os.path.join(os.sep, script_dir,"Data/service")
ptcleanservice = os.path.join(os.sep, script_dir,"Data/serviceclean.json")


def stringIsLatin(s):
    return all([c in string.printable for c in s])

def loadAllData():      
    with open(ptall, "r", encoding="utf8") as f:
        s = f.read()
        return json.loads(s)

def loadCleanServiceData():
    with open(ptcleanservice, "r", encoding="utf8") as f:
        s = f.read()
        return json.loads(s)

            
def pickRandomFile(lodata):
    n = len(lodata)
    return random.randint(0,n-1)

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

############################################################################3
#These function do not need to be used anymore, were used to inspect the data
# and to clean the data as well, used to create serviceclean.

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

def loadAllServiceData():
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
    return lodata
    
def cleanData(lodata):
    newdict = {}
    for rev in lodata:
        try:
            if rev["urls"] and rev["pointsData"]:
                newdict[rev["urls"][0]] = rev
        except:
            pass
    return newdict

def saveJson(adict, filename, path = ''):
    with open(path + filename+ '.json', 'w') as outfile:
        json.dump(adict, outfile)
    