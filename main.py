#%% First, let's import the necessary packages.

import pandas as pd
import numpy as np
import os
os.chdir(r'C:\Users\jptth\Documents\GitHub\Momentum')
import sys
import time
import Header
from sklearn import linear_model as skl
premium_api = "8NIR58ZCJWT4MFNH"
filepath = os.getcwd()
os.chdir('../../GitHub Data')
#%% Now, we import the necessary data for the SmallCap model. 
# This data comes from the Data_collection code.
# the double "%" is a Spyder feature, that separates code into executable cells.
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
# We can get a list of companies by taking the columns from one of these and cleaning:
Companies = pd.DataFrame(ME_clean.columns,columns= ['Company name'])
# We only use dates that are in all of our datasets.
SE_Dates = pd.DataFrame(SE_clean.index)
RSI_Dates = pd.DataFrame(RSI_clean.index)
ME_Dates = pd.DataFrame(ME_clean.index)
Profit_Dates = pd.DataFrame(Profit_clean.index)
Beta_Dates = pd.DataFrame(Beta_clean.index)
Dates = pd.merge(SE_Dates, RSI_Dates, how='inner', on=['EOMONTH'])
Dates = pd.merge(Dates, ME_Dates, how='inner', on=['EOMONTH'])
Dates = Dates.reindex(index=Dates.index[::-1]).reset_index(drop=True)
del(SE_Dates, RSI_Dates, ME_Dates, Profit_Dates, Beta_Dates)

#%% We aim to construct a for loop, across a range of dates.
# For each date, the code will create a regression model of the previous 2 years, to determine which factors are significant.
# For our loop, we drop the first 23 dates. This is because each regression model will work on the last 2 years.
Executable_Dates = Dates[23:]
Coefficient_timeline = pd.DataFrame(columns=['RSI','VAL','GP','Beta'], index=Executable_Dates['EOMONTH'])
Dataset = pd.DataFrame()
Purchases = pd.DataFrame(columns=['1st Choice','2nd Choice','3rd Choice'], index=Executable_Dates['EOMONTH'])
for a in Executable_Dates.index:
    print(str(a)+'- '+Executable_Dates.at[a,'EOMONTH'])
    end_date = Executable_Dates.at[a,'EOMONTH']
    chosen_dates = Dates[a-23:a+1]
    snapshot = Header.snapshot(end_date, Companies, ME_clean, SE_clean, RSI_clean, Profit_clean, Beta_clean)
    for company_name in Companies['Company name']:
        Company_df = Header.company_dataset(company_name, chosen_dates, ME_clean, SE_clean, RSI_clean, Profit_clean, Beta_clean)
        Company_df = Company_df.add_prefix(company_name+' ',axis=0)
        Dataset = pd.concat([Dataset, Company_df])
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
    Coefficient_timeline.loc[end_date] = coefficients
    snapshot['PME'] = (
        reg.intercept_ + 
        coefficients[0] * snapshot['RSI'] + 
        coefficients[1] * snapshot['VAL'] +
        coefficients[2] * snapshot['GP'] +
        coefficients[3] * snapshot['Beta']
        )
    snapshot['Rank'] = len(snapshot) + 1 - snapshot['PME'].rank()
    snapshot['Companies'] = snapshot.index
    Purchases.at[end_date,'1st Choice'] = snapshot.set_index('Rank').at[1,'Companies']
    Purchases.at[end_date,'2nd Choice'] = snapshot.set_index('Rank').at[2,'Companies']
    Purchases.at[end_date,'3rd Choice'] = snapshot.set_index('Rank').at[3,'Companies']
    
    
