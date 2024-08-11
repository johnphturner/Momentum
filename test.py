# -*- coding: utf-8 -*-
"""
Created on Tue Aug  6 15:21:00 2024

@author: jptth
"""
import pandas as pd
import numpy as np
import os
import sys
from urllib.request import Request, urlopen
import json
import time
import calendar
from matplotlib import pyplot as plt
from sklearn import linear_model as skl
premium_api = "8NIR58ZCJWT4MFNH"
import Header as Header
filepath = os.getcwd()

SE_clean = pd.read_csv(
    'C:/Users/jptth/PycharmProjects/Momentum/Data/Collection Code Output/FTSE SmallCap SE Clean.csv',
    index_col='EOMONTH'
    )
SE_normalised = Header.normalise_df(SE_clean)
RSI_clean = pd.read_csv(
    'C:/Users/jptth/PycharmProjects/Momentum/Data/Collection Code Output/AV- FTSE SmallCap RSI.csv',
    index_col='EOMONTH'
    )
RSI_normalised = Header.normalise_df(RSI_clean)

ME_clean = pd.read_csv(
    'C:/Users/jptth/PycharmProjects/Momentum/Data/Collection Code Output/AV-FTSE SmallCap ME.csv',
    index_col='EOMONTH'
    )
ME_normalised = Header.normalise_df(ME_clean)

Dates = pd.DataFrame(
    SE_clean.index
    )
Date = "2019-12-31"

company_name = "CAPITA PLC"
df = pd.DataFrame(index=Dates)
df['SE'] = SE_normalised["SE- "+company_name]
df["RSI"] = RSI_normalised["RSI- "+company_name]
df['ME'] = ME_normalised['ME- '+company_name]
df['value'] = df['ME'].div(df['SE'])

def company_dataset(company_name,
                    dates,
                    ME_clean,
                    SE_clean,
                    RSI_clean
                    ):
    df = pd.DataFrame(index=dates)
    df['ME'] = ME_clean['ME- '+company_name].astype(float)
    df['RSI'] = RSI_clean['RSI- '+company_name]
    df['MOM'] = Header.normalise_column(df['RSI'])
    df['VAL'] = SE_clean['SE- '+company_name].div(ME_clean['ME- '+company_name])
    df['HML'] = Header.normalise_column(df['VAL'])
    df.drop(['VAL', 'RSI'], axis=1, inplace=True)
    return df