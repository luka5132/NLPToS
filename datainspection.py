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
import pandas
from bs4 import BeautifulSoup
import trafilatura


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

            
def pickRandomFile(datadict):
    return random.choice(list(datadict.values()))

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

def getFullUrl(url):
    if url.startswith("https://www."):
        return url
    elif url.startswith("www."):
        return "https://" + url
    else:
        return "https://www." + url
    
    
def getColumnnames(datadict):
    initialset = set()
    pdset = set()
    for fkeys in datadict:
        afile = datadict[fkeys]
        inkeys = afile.keys()
        for akey in inkeys:
            initialset.add(akey)
        pd = afile["pointsData"]
        for pdid in pd:
            pi = pd[pdid]
            for p in pi:
                pdset.add(p)
            try:
                tosdr = pi["tosdr"]
                for tosdrkey in tosdr:
                    pdset.add(tosdrkey)
            except:
                pass
    return list(initialset) + list(pdset)

colnames = ['url','alexa', 'class', 'id','quote','quoteDoc','quoteText',
            'title',"source", 'binding','score',"point", "case"]
    
def tryfromdict(adict, poskey):
    try:
        return adict[poskey]
    except:
        return None
    
l1 = ["url","alexa","class"]
l2 = ["id","quote","quoteDoc","quoteText","title","source"]
l3 = ['binding','score',"points", "case"]

def dicttocsv(adict, columnnames):
    pddf = pandas.DataFrame(columns = columnnames)
    l1 = ["url","alexa","class"]
    l2 = ["id","quote","quoteDoc","quoteText","title","source"]
    l3 = ['binding','score',"point", "case"]
    l2l3len = len(columnnames) - 3
    pddf_i = 0
    for keyname in adict.keys():
        l1list = [None] * 3
        newkeyname = getFullUrl(keyname)
        l1list[0] = newkeyname
        afile = adict[keyname]
        i = 1
        for point1 in l1[1:]:
            a = tryfromdict(afile,point1)
            if a:
                l1list[i] = a
            i +=1
        apd = afile["pointsData"]
        for pdid in apd:
            point = apd[pdid]
            index = 0
            l2l3list = [None] * l2l3len
            for point2 in l2:
                b = tryfromdict(point,point2)
                if b:
                    l2l3list[index] = b
                index += 1
            try:
                tosdr = point["tosdr"]
                for point3 in l3:
                    c = tryfromdict(tosdr,point3)
                    if c:
                        l2l3list[index] = c
                    index +=1
            except:
                pass
            newrow = l1list + l2l3list
            pddf.loc[pddf_i] = newrow
            pddf_i += 1
            
    return pddf
        
                        
def cleanText(s):
    return trafilatura.extract(s).replace("\n",'')

def cleanColumn(pddf, colname):
    col = pddf[colname]
    collist = []
    for text in col:
        try:
            collist.append(cleanText(text))
        except:
            collist.append('')
    return collist

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

path = r"C:\Users\luka5132\Documents\GitHub\NLPToS"

def saveJson(adict, filename, path = ''):
    with open(path + filename+ '.json', 'w') as outfile:
        json.dump(adict, outfile)
        
def saveCSV(adf, filename, path = path):
    adf.to_csv (path + filename + ".csv", index = False, header=True)
    