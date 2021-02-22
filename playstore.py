# -*- coding: utf-8 -*-
"""
Created on Sun Feb 21 17:47:27 2021

@author: luka5132
"""

import pandas
import os
import string
import re
import datainspection as di
import locale
locale.setlocale( locale.LC_ALL, 'en_US.UTF-8' ) 

script_dir = os.getcwd()
pttoplaydata = os.path.join(os.sep, script_dir,"Data/playstore/Google-Playstore.csv")

def loadPlaystore():
    return pandas.read_csv(pttoplaydata)

LOAD = False
if LOAD:
    play_df = loadPlaystore()

def colStringToFloat(adf, colname):
    col = adf[colname]
    
    def returnFloat(var):
        if isinstance(var, str):
            return locale.atoi(var[:-1])
        else:
            return var
    
    return [returnFloat(x) for x in col]

subdf = play_df[play_df["Intinstalls"] > 50000]


print(subdf[:5], len(subdf))
