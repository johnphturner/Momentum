# First, let's import the necessary packages.
import pandas as pd
import numpy as np
import os
import sys
import time
import Header
premium_api = "8NIR58ZCJWT4MFNH"
filepath = os.getcwd()
#%% Now, we import the necessary data.
# This data comes from the Data_collection code.
# the double "%" is a Spyder feature, that separates code into executable cells.

SE_clean = pd.read_csv(
    'C:/Users/jptth/PycharmProjects/Momentum/Data/Collection Code Output/FTSE SmallCap SE Clean.csv',
    index_col='EOMONTH'
    )
RSI_clean = pd.read_csv(
    'C:/Users/jptth/PycharmProjects/Momentum/Data/Collection Code Output/AV- FTSE SmallCap RSI.csv',
    index_col='EOMONTH'
    )
ME_clean = pd.read_csv(
    'C:/Users/jptth/PycharmProjects/Momentum/Data/Collection Code Output/AV-FTSE SmallCap ME.csv',
    index_col='EOMONTH'
    )
# We only use dates that are in all of our datasets.
SE_Dates = pd.DataFrame(SE_clean.index)
RSI_Dates = pd.DataFrame(RSI_clean.index)
ME_Dates = pd.DataFrame(ME_clean.index)
Dates = pd.merge(SE_Dates, RSI_Dates, how='inner', on=['EOMONTH'])
Dates = pd.merge(Dates, ME_Dates, how='inner', on=['EOMONTH'])


#%% We aim to construct a for loop, across a range of dates.
# For each date, the code will create a regression model of the previous 2 years, to determine which factors are significant.
# 
# For our loop, we drop the bottom 23 dates. This is because each regression model will work on the last 2 years.
Executable_Dates = Dates[:-24]