# -*- coding: utf-8 -*-
"""
Created on Tue Aug  6 15:21:00 2024

@author: jptth
"""
import pandas as pd
import numpy as np
import os
os.chdir(r'C:\Users\jptth\Documents\GitHub\Momentum')
import sys
from urllib.request import Request, urlopen
import json
import time
import calendar
from matplotlib import pyplot as plt
from sklearn import linear_model as skl
premium_api = "8NIR58ZCJWT4MFNH"
import Header
os.chdir('../../GitHub Data')
filepath = os.getcwd()

SE_clean = pd.read_csv(
    'Collection Code Output/FTSE SmallCap SE Clean.csv',
    index_col='EOMONTH'
    )

RSI_clean = pd.read_csv(
    'Collection Code Output/AV- FTSE SmallCap RSI.csv',
    index_col='EOMONTH'
    )

ME_clean = pd.read_csv(
    'Collection Code Output/AV- FTSE SmallCap ME.csv',
    index_col='EOMONTH'
    )

Profit_clean = pd.read_csv(
    'Collection Code Output/FTSE SmallCap Profit Clean.csv',
    index_col='EOMONTH'
    )
Companies = pd.DataFrame(ME_clean.columns.str.removeprefix('ME- '),columns= ['Company name'])
Dates = pd.DataFrame(
    SE_clean.index
    )
chosen_dates = Dates[12:27]
Date = "2019-12-31"
Dataset = pd.DataFrame()
for company_name in Companies['Company name']:
    x = Header.company_dataset(company_name, chosen_dates, ME_clean, SE_clean, RSI_clean, Profit_clean)
    x = x.add_prefix(company_name+' ',axis=0)
    Dataset = pd.concat([Dataset, x])
    