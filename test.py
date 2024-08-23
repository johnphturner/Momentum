# -*- coding: utf-8 -*-
"""
Created on Tue Aug  6 15:21:00 2024

@author: jptth
"""
#%% Modules and filepaths
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
#%% Data

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
Beta_clean = pd.read_csv(
    'Collection Code Output/FTSE SmallCap Beta.csv',
    index_col='EOMONTH'
    )
#%% From main.py:
# We can get a list of companies by taking the columns from one of these and cleaning:
Companies = pd.DataFrame(ME_clean.columns.str.removeprefix('ME- '),columns= ['Company name'])
# We only use dates that are in all of our datasets.
SE_Dates = pd.DataFrame(SE_clean.index)
RSI_Dates = pd.DataFrame(RSI_clean.index)
ME_Dates = pd.DataFrame(ME_clean.index)
Profit_Dates = pd.DataFrame(Profit_clean.index)
Beta_Dates = pd.DataFrame(Beta_clean.index)
Dates = pd.merge(SE_Dates, RSI_Dates, how='inner', on=['EOMONTH'])
Dates = pd.merge(Dates, ME_Dates, how='inner', on=['EOMONTH'])
Dates = Dates.reindex(index=Dates.index[::-1]).reset_index(drop=True)
#%% Experimenting with one loop
chosen_dates = Dates[34:58]
Date = "2019-12-31"
Dataset = pd.DataFrame()
# Coefficient_timeline = pd.DataFrame(columns=['RSI','VAL','GP','Beta'])
for company_name in Companies['Company name']:
    Company_df = Header.company_dataset(company_name, chosen_dates, ME_clean, SE_clean, RSI_clean, Profit_clean, Beta_clean)
    Company_df = Company_df.add_prefix(company_name+' ',axis=0)
    Dataset = pd.concat([Dataset, Company_df])


snapshot = Header.snapshot(Date, Companies, ME_clean, SE_clean, RSI_clean, Profit_clean, Beta_clean)
ranking_snapshot = snapshot.rank()
reg = skl.Lasso(alpha=1)
Dataset['VAL']= Header.normalise_column(Dataset['VAL'],flt=True)
x = Dataset[['RSI','VAL','GP','Beta']]
y = Dataset['ME']
reg.fit(x,y)
coefficients = reg.coef_
for idx, coef in enumerate(coefficients):
    if coefficients[idx]==0:
        print(f"{x.columns[idx]}: Insignificant")
    else:
        print(f"{x.columns[idx]}: Coefficient {coef}")

def Dataset(Companies, chosen_dates, ME, SE, RSI, Profit, Beta):
    for company_name in Companies['Company name']:
        Dataset = pd.DataFrame()
        Company_df = Header.company_dataset(company_name, chosen_dates, ME, SE, RSI, Profit, Beta)
        Company_df = Company_df.add_prefix(company_name+' ',axis=0)
        Dataset = pd.concat([Dataset, Company_df])
        return Dataset

#%% Experimenting with inputs

x = input('Gimme a bullet to bite on: ')
try:
    int_x = int(x)
except ValueError as verr:
  x = input('Gimme a bullet to bite on: ')
except Exception as ex:
  x = input('Something to chew')

#%% Experimenting with KPI:
    
# Let's make a matrix that shows what buying a stock for £1 and holding for n months looks like.
hold_for=3
# First we reorder.
ME_ordered = ME_clean.loc[Dates['EOMONTH'].loc[hold_for:]]
# Now, we make a matrix shifted n-dates into the future, for the returns.
ME_shifted = ME_ordered.shift(-hold_for)
# This gives us a payoff matrix:
stock_movement = (ME_shifted - ME_ordered)
# But we need to divide through by the initial stock price, so it's just a £1 bet.
Payoff = stock_movement.div(ME_ordered)

