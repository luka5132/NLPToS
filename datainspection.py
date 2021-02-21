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
from langdetect import detect



script_dir = os.getcwd()
ptall = os.path.join(os.sep, script_dir,"Data/all.json")
ptservice = os.path.join(os.sep, script_dir,"Data/service")
ptcleanservice = os.path.join(os.sep, script_dir,"Data/serviceclean.json")
quotespath = os.path.join(os.sep, script_dir,"Data/quotes.csv")
textspath = os.path.join(os.sep, script_dir,"Data/texts.csv")




def stringIsLatin(s):
    return all([c in string.printable for c in s])

def stringIsEnglish(s):
    try:
        return detect(s) == "en"
    except:
        return False

def loadAllData():      
    with open(ptall, "r", encoding="utf8") as f:
        s = f.read()
        return json.loads(s)

def loadCleanServiceData():
    with open(ptcleanservice, "r", encoding="utf8") as f:
        s = f.read()
        return json.loads(s)
    
def loadQuotes():
    return pandas.read_csv(quotespath)

def pickRandomJsonFile(datadict):
    return random.choice(list(datadict.values()))

def pickRandomCsvFile(pddf, n = 1):
    allurls = pddf.url.unique()
    urllist = []
    for i in range(n):
        urllist.append(random.choice(allurls))
        
    return pddf[pddf.url.isin(urllist)]

def loadTexts():
    return pandas.read_csv(textspath, encoding="unicode_escape")
    

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

def addUrl(url):
    if url.startswith("https://www.") or url.startswith("https://"):
        return url
    elif url.startswith("www."):
        return "https://" + url
    else:
        return "https://www." + url
    
def getFullUrl(url, link):
    if link:
        if "." not in link:
            return addUrl(url) + link
        else:
            return addUrl(link)
    else: return url


def stemUrl(url):
    domains = [".com", ".org", ".net", ".edu", ".gov"]
    domname = None
    i = 0
    while not domname and i < len(domains):
        dom = domains[i]
        if dom in url:
            domname = dom
        i +=1
    if domname:
        parts = url.partition(dom)
        return parts[0] + parts[1]
    else:
        return url
    
    
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


def removeWeirdBit(text):
    weirdletter = "Â"
    try:
        l_i = text.index(weirdletter)
        p1 = text[:l_i]
        return p1 + removeWeirdBit(text[l_i+2:])
    except:
        return text
    
def cleanText(text):
    "cleans text"
    clean = re.compile('<.*?>')
    nohtml =  re.sub(clean, '', text).replace("\n",'')
    noweirdbit = removeWeirdBit(nohtml)
    return ''.join(filter(lambda x: x in string.printable, noweirdbit))


def cleanColumn(pddf, colname):
    col = pddf[colname]
    collist = []
    for text in col:
        try:
            collist.append(cleanText(text))
        except:
            collist.append('')
    return collist

def removeNonEnglish(pddf):
    englishtext = [s for s in pddf["quoteText"] if stringIsEnglish(s)]
    return pddf[pddf.quoteText.isin(englishtext)]

def getLinksFromDict(adict):
    linkslist = []
    for rev in adict:
        file = adict[rev]
        if file["links"]:
            try:
                for link in file["links"].values():
                    url = link["url"]
                    linkslist.append(url)
            except:
                pass
    
    return linkslist

def websiteAndLlinks(adict):
    links = getLinksFromDict(adict)
    linksdict = {}
    for link in links:
        stemmed = stemUrl(link)
        if stemmed in linksdict:
            linksdict[stemmed].append(link)
        else:
            linksdict[stemmed] = [link]
    return linksdict


        

############################################################################3
#These function do not need to be used anymore, were used to inspect the data
# and to clean the data as well, used to create serviceclean.

def inspectData(lodata):
    infdict = {}
    pagesrefferenced = 0
    totquotes = 0
    typeset = set()
    for revkey in lodata:
        rev = lodata[revkey]
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
                typeset.add(type(point["quoteDoc"]))
            except:
                print(point)
        pagesrefferenced += len(webpages)
        
        revdict["webpages"] = webpages
        revdict["nqt"] = nquotes
        infdict[url] = revdict
        
    infdict["totpages"] = pagesrefferenced
    infdict["totquotes"] = totquotes
    infdict["types"] = typeset
    
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

path = r"C:\Users\luka5132\Documents\GitHub\NLPToS\data\\"

def saveJson(adict, filename, path = ''):
    with open(path + filename+ '.json', 'w') as outfile:
        json.dump(adict, outfile)
        
def saveCSV(adf, filename, path = path):
    adf.to_csv (path + filename + ".csv", index = False, header=True)
    
from difflib import SequenceMatcher



# Code taken form stackoverflow:
# https://stackoverflow.com/questions/36013295/find-best-substring-match
def get_best_match(query, corpus, step=4, flex=3, case_sensitive=False, verbose=False):
    """Return best matching substring of corpus.

    Parameters
    ----------
    query : str
    corpus : str
    step : int
        Step size of first match-value scan through corpus. Can be thought of
        as a sort of "scan resolution". Should not exceed length of query.
    flex : int
        Max. left/right substring position adjustment value. Should not
        exceed length of query / 2.

    Outputs
    -------
    output0 : str
        Best matching substring.
    output1 : float
        Match ratio of best matching substring. 1 is perfect match.
    """

    def _match(a, b):
        """Compact alias for SequenceMatcher."""
        return SequenceMatcher(None, a, b).ratio()

    def scan_corpus(step):
        """Return list of match values from corpus-wide scan."""
        match_values = []

        m = 0
        while m + qlen - step <= len(corpus):
            match_values.append(_match(query, corpus[m : m-1+qlen]))
            if verbose:
                print(query, "-", corpus[m: m + qlen], _match(query, corpus[m: m + qlen]))
            m += step

        return match_values

    def index_max(v):
        """Return index of max value."""
        return max(range(len(v)), key=v.__getitem__)

    def adjust_left_right_positions():
        """Return left/right positions for best string match."""
        # bp_* is synonym for 'Best Position Left/Right' and are adjusted 
        # to optimize bmv_*
        p_l, bp_l = [pos] * 2
        p_r, bp_r = [pos + qlen] * 2

        # bmv_* are declared here in case they are untouched in optimization
        bmv_l = match_values[p_l // step]
        bmv_r = match_values[p_l // step]

        for f in range(flex):
            ll = _match(query, corpus[p_l - f: p_r])
            if ll > bmv_l:
                bmv_l = ll
                bp_l = p_l - f

            lr = _match(query, corpus[p_l + f: p_r])
            if lr > bmv_l:
                bmv_l = lr
                bp_l = p_l + f

            rl = _match(query, corpus[p_l: p_r - f])
            if rl > bmv_r:
                bmv_r = rl
                bp_r = p_r - f

            rr = _match(query, corpus[p_l: p_r + f])
            if rr > bmv_r:
                bmv_r = rr
                bp_r = p_r + f

            if verbose:
                print("\n" + str(f))
                print("ll: -- value: %f -- snippet: %s" % (ll, corpus[p_l - f: p_r]))
                print("lr: -- value: %f -- snippet: %s" % (lr, corpus[p_l + f: p_r]))
                print("rl: -- value: %f -- snippet: %s" % (rl, corpus[p_l: p_r - f]))
                print("rr: -- value: %f -- snippet: %s" % (rl, corpus[p_l: p_r + f]))

        return bp_l, bp_r, _match(query, corpus[bp_l : bp_r])

    if not case_sensitive:
        query = query.lower()
        corpus = corpus.lower()

    qlen = len(query)

    if flex >= qlen/2:
        print("Warning: flex exceeds length of query / 2. Setting to default.")
        flex = 3

    match_values = scan_corpus(step)
    pos = index_max(match_values) * step

    pos_left, pos_right, match_value = adjust_left_right_positions()

    return corpus[pos_left: pos_right].strip(), match_value
    