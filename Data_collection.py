import pandas as pd
import numpy as np
import os
import sys
import time
import Header
premium_api = "8NIR58ZCJWT4MFNH"
filepath = os.getcwd()

# <editor-fold desc="Raw Data for FTSE SmallCap Collection">

SmallCap_df_raw = pd.read_excel(
    'Data/FTSE SmallCap Tickers.xlsx',
    sheet_name='Results',
    )

# We drop the private/ discontinued stocks:
# "HOME REIT PLC","THE DIVERSE INCOME TRUST PLC","ABERFORTH SPLIT LEVEL INCOME TRUST PLC",
# "HENDERSON EUROTRUST PLC", "ABRDN NEW DAWN INVESTMENT TRUST PLC"
SmallCap_df_raw.drop(
    [46, 51, 60, 65, 76],
    inplace=True
    )
SmallCap_df_raw.drop(
    "Unnamed: 0",
    axis="columns",
    inplace=True
    )
SmallCap_df_raw.reset_index(
    drop=True,
    inplace=True
)
tickers = SmallCap_df_raw["Ticker symbol"]
companies = SmallCap_df_raw["Company name"]

# </editor-fold>

# <editor-fold desc="Small Cap Stock Prices">

API = Header.sourcing_alphavantage_data(
    companies,
    tickers,
    premium_api,
    'close',
    'TIME_SERIES_MONTHLY_ADJUSTED'
)
EOMONTH = Header.index_dates_to_end_of_month(API.set_index(API["timestamp"], drop=True))
EOMONTH.to_csv("Data/Collection Code Output/AV- FTSE SmallCap ME.csv")
del API

# </editor-fold>

# <editor-fold desc="Small Cap RSI">

API = Header.iterating_through_RSI(companies, tickers, premium_api)
API = API.bfill()
API = API.fillna('50')
API.to_csv("Data/Collection Code Output/AV- FTSE SmallCap RSI.csv")
del API
# </editor-fold>

# <editor-fold desc="Small Cap Shareholder Equities">

SmallCap_SE_raw = pd.read_excel(
    'Data/FTSE Small Cap SE.xlsx',
    sheet_name='Results',
    index_col='Company name'
    )
SmallCap_SE_raw.drop(
    [
        "HOME REIT PLC",
        "BLACKROCK FRONTIERS INVESTMENT TRUST PLC",
        "ABERFORTH SPLIT LEVEL INCOME TRUST PLC",
        "HENDERSON EUROTRUST PLC",
        "ABRDN NEW DAWN INVESTMENT TRUST PLC"
    ],
    inplace=True
    )
clean_df = Header.clean_SE_data(SmallCap_SE_raw)
month_df = Header.financial_year_to_monthly(clean_df)
month_df.drop(
    [
        "March 2025",
        "February 2025",
        "January 2025",
        "December 2024",
        "November 2024",
        "October 2024",
        "September 2024"
    ],
    axis=0,
    inplace=True
)
number_month_df = Header.month_year_to_eomonth(month_df)
number_month_df = number_month_df.replace(to_replace='n.a.', value=np.nan).bfill().fillna('0')
number_month_df.add_prefix('SE- ', axis=1).to_csv("Data/Collection Code Output/FTSE SmallCap SE Clean.csv")
del(SmallCap_SE_raw, clean_df, month_df, number_month_df)
# </editor-fold>

del(companies, tickers, SmallCap_df_raw)

# <editor-fold desc="Raw Data for FTSE 100 Collection">

FTSE_df_raw = pd.read_excel(
    'Data/FTSE 100 Tickers.xlsx',
    sheet_name='Results',
    )
# We drop the stocks for which we can't find the tickers:
# "BT"
FTSE_df_raw.drop(
    [19],
    inplace=True
    )
FTSE_df_raw.drop(
    "Unnamed: 0",
    axis="columns",
    inplace=True
    )
FTSE_df_raw.reset_index(
    drop=True,
    inplace=True
)
tickers = FTSE_df_raw["Ticker symbol"]
companies = FTSE_df_raw["Company name"]

# </editor-fold>

# <editor-fold desc="Large Cap Stock Prices">

API = Header.sourcing_alphavantage_data(
    companies,
    tickers,
    premium_api,
    'close',
    'TIME_SERIES_MONTHLY_ADJUSTED'
)
EOMONTH = Header.index_dates_to_end_of_month(API.set_index(API["timestamp"], drop=True))
EOMONTH.to_csv("Data/Collection Code Output/AV- FTSE 100 ME.csv")
del(API, EOMONTH)

# </editor-fold>

# <editor-fold desc="Large Cap RSI">


API = Header.iterating_through_RSI(
    companies,
    tickers,
    premium_api
)
API = API.bfill()
API = API.fillna('50')
API.to_csv("Data/Collection Code Output/AV- FTSE 100 RSI.csv")

# </editor-fold>

# <editor-fold desc="Large Cap Shareholder Equities">
FTSE_SE_raw = pd.read_excel(
    'Data/FTSE 100 SE.xlsx',
    sheet_name='Results',
    index_col='Company name'
    )
FTSE_SE_raw.drop(
    [19],
    inplace=True
    )
clean_df = Header.clean_SE_data(FTSE_SE_raw)
month_df = Header.financial_year_to_monthly(clean_df)
month_df.drop(
    [
        "March 2025",
        "February 2025",
        "January 2025",
        "December 2024",
        "November 2024",
        "October 2024",
        "September 2024"
    ],
    axis=0,
    inplace=True
)
number_month_df = Header.month_year_to_eomonth(month_df)
number_month_df.add_prefix('SE- ', axis=1).to_csv("Data/Collection Code Output/FTSE 100 SE Clean.csv")
number_month_df = number_month_df.replace(to_replace='n.a.', value=np.nan).bfill().fillna('0')
del(FTSE_SE_raw, clean_df, month_df, number_month_df)
# </editor-fold>

del(companies, tickers, FTSE_df_raw)

print("SUCCESS")