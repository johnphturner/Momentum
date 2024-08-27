# %% 1. This file is separated into cells so one can just run the imports and then the cell one wants to update.
import os

os.chdir(r"C:\Users\jptth\Documents\GitHub\Momentum")
import pandas as pd
import numpy as np
import sys
import time
import Header

premium_api = "8NIR58ZCJWT4MFNH"

filepath = os.getcwd()
# %% 2. Raw Data for FTSE SmallCap Collection

os.chdir(r"C:\Users\jptth\Documents\GitHub Data")
# Tickers- table created on FAME by filtering for stock data>FTSE indexes>FTSE SmallCap, stock data>listed/unlisted>listed.
# I then added the column identifiers>ticker symbol
SmallCap_df_raw = pd.read_excel(
    "FTSE SmallCap Tickers.xlsx",
    sheet_name="Results",
)

# We drop the private/ discontinued stocks:
# "HOME REIT PLC","THE DIVERSE INCOME TRUST PLC","ABERFORTH SPLIT LEVEL INCOME TRUST PLC",
# "HENDERSON EUROTRUST PLC", "HENDERSON EUROPEAN TRUST PLC" "ABRDN NEW DAWN INVESTMENT TRUST PLC"
SmallCap_df_raw.drop([46, 51, 59, 60, 65, 76, 101], inplace=True)
SmallCap_df_raw.drop("Unnamed: 0", axis="columns", inplace=True)
SmallCap_df_raw.reset_index(drop=True, inplace=True)
tickers = SmallCap_df_raw["Ticker symbol"]
companies = SmallCap_df_raw["Company name"]

# %% 3. Small Cap Stock Prices

os.chdir(r"C:\Users\jptth\Documents\GitHub Data")
API = Header.sourcing_alphavantage_data(
    companies, tickers, premium_api, "close", "TIME_SERIES_MONTHLY_ADJUSTED"
)
EOMONTH = Header.index_dates_to_end_of_month(API.set_index(API["timestamp"], drop=True))
EOMONTH = EOMONTH.replace(0, np.nan).bfill().ffill().fillna(1)
EOMONTH.to_csv("Collection Code Output/AV- FTSE SmallCap ME.csv")
del API

# %% 4. Small Cap RSI

os.chdir(r"C:\Users\jptth\Documents\GitHub Data")
API = Header.iterating_through_RSI(companies, tickers, premium_api)
API = API.bfill()
API = API.fillna("50")
API.to_csv("Collection Code Output/AV- FTSE SmallCap RSI.csv")
del API
# %% 5. Small Cap Shareholder Equities

# table created on FAME by filtering for stock data>FTSE indexes>FTSE SmallCap, stock data>listed/unlisted>listed.
# I then added the columns financials and ratios>balance sheet>shareholder funds.
os.chdir(r"C:\Users\jptth\Documents\GitHub Data")
SmallCap_SE_raw = pd.read_excel(
    "FTSE Small Cap SE.xlsx", sheet_name="Results", index_col="Company name"
)
SmallCap_SE_raw.drop(
    [
        "HOME REIT PLC",
        "BLACKROCK FRONTIERS INVESTMENT TRUST PLC",
        "ABERFORTH SPLIT LEVEL INCOME TRUST PLC",
        "HENDERSON EUROTRUST PLC",
        "ABRDN NEW DAWN INVESTMENT TRUST PLC",
        "HENDERSON EUROPEAN TRUST PLC",
        "INVESCO GLOBAL EQUITY INCOME TRUST PLC",
    ],
    inplace=True,
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
        "September 2024",
    ],
    axis=0,
    inplace=True,
)
number_month_df = Header.month_year_to_eomonth(month_df)
number_month_df = (
    number_month_df.replace(to_replace="n.a.", value=np.nan).bfill().ffill()
)
number_month_df.add_prefix("SE- ", axis=1).to_csv(
    "Collection Code Output/FTSE SmallCap SE Clean.csv"
)
del (SmallCap_SE_raw, clean_df, month_df)

# %% 6. Small Cap Profit

# table created on FAME by filtering for stock data>FTSE indexes>FTSE SmallCap, stock data>listed/unlisted>listed.
# I then added the columns financials and ratios>balance sheet>profit and loss account.
os.chdir(r"C:\Users\jptth\Documents\GitHub Data")
SmallCap_profit_raw = pd.read_excel(
    "FTSE SmallCap Profit.xlsx", sheet_name="Results", index_col="Company name"
)
SmallCap_profit_raw.drop(
    [
        "HOME REIT PLC",
        "BLACKROCK FRONTIERS INVESTMENT TRUST PLC",
        "ABERFORTH SPLIT LEVEL INCOME TRUST PLC",
        "HENDERSON EUROTRUST PLC",
        "ABRDN NEW DAWN INVESTMENT TRUST PLC",
        "HENDERSON EUROPEAN TRUST PLC",
        "INVESCO GLOBAL EQUITY INCOME TRUST PLC",
    ],
    inplace=True,
)
clean_df = Header.clean_profit_data(SmallCap_profit_raw)
month_df = Header.financial_year_to_monthly(clean_df)
month_df.drop(
    [
        "March 2025",
        "February 2025",
        "January 2025",
        "December 2024",
        "November 2024",
        "October 2024",
        "September 2024",
    ],
    axis=0,
    inplace=True,
)
number_month_df = Header.month_year_to_eomonth(month_df)
number_month_df = (
    number_month_df.replace(to_replace=["n.a.", "n.s."], value=np.nan)
    .bfill()
    .fillna("0")
)
number_month_df.add_prefix("Profit- ", axis=1).to_csv(
    "Collection Code Output/FTSE SmallCap Profit Clean.csv"
)
del (SmallCap_profit_raw, clean_df, month_df, number_month_df)

# %% 7. We calculate the beta from the stock price.

os.chdir(r"C:\Users\jptth\Documents\GitHub Data")
first_date = EOMONTH.index[-1]
Returns = pd.DataFrame(index=EOMONTH.index)
Beta = pd.DataFrame(index=EOMONTH.index)
Returns["Revenue- Total"] = EOMONTH.sum(axis=1)
first_total_price = Returns.at[first_date, "Revenue- Total"]
Returns["Beta- Total"] = (
    Returns["Revenue- Total"] - first_total_price
) / first_total_price
dates = pd.DataFrame(EOMONTH.index)
for i in EOMONTH.columns:
    first_price = EOMONTH.at[first_date, i]
    Returns[i] = (EOMONTH[i] - first_price) / first_price
for i in EOMONTH.columns:
    for a in dates[:-22].index:
        end_date = dates.at[a, "EOMONTH"]
        test_range = Returns[a : a + 23]
        if test_range[i].var() == 0:
            Beta.loc[end_date, "Beta- " + i] = 0
        else:
            Beta.loc[end_date, "Beta- " + i] = (
                test_range.cov().at["Beta- Total", i]
            ) / (test_range[i].var())
    for a in dates[-22:-1].index:
        end_date = dates.at[a, "EOMONTH"]
        test_range = Returns[a:]
        if test_range[i].var() == 0:
            Beta.loc[end_date, "Beta- " + i] = 0
        else:
            Beta.loc[end_date, "Beta- " + i] = (
                test_range.cov().at["Beta- Total", i]
            ) / (test_range[i].var())
    end_date = dates.at[len(dates) - 1, "EOMONTH"]
    Beta.loc[end_date, "Beta- " + i] = 0
Beta.to_csv("Collection Code Output/FTSE SmallCap Beta.csv")
del (EOMONTH, Beta, Returns, first_date, first_price, first_total_price, test_range)

# %% 8. SmallCap data collection has finished. We clear the variables for the FTSE 100:

del (companies, tickers, SmallCap_df_raw)
# %% 9. Raw Data for FTSE 100 Collection

# table created on FAME by filtering for stock data>FTSE indexes>FTSE 100, stock data>listed/unlisted>listed.
# I then added the column identifiers>ticker symbol.
os.chdir(r"C:\Users\jptth\Documents\GitHub Data")
FTSE_df_raw = pd.read_excel(
    "FTSE 100 Tickers.xlsx",
    sheet_name="Results",
)
# We drop the stocks for which we can't find the tickers:
# "BT"
FTSE_df_raw.drop([19], inplace=True)
FTSE_df_raw.drop("Unnamed: 0", axis="columns", inplace=True)
FTSE_df_raw.reset_index(drop=True, inplace=True)
tickers = FTSE_df_raw["Ticker symbol"]
companies = FTSE_df_raw["Company name"]

# %% 10. Large Cap Stock Prices

os.chdir(r"C:\Users\jptth\Documents\GitHub Data")
API = Header.sourcing_alphavantage_data(
    companies, tickers, premium_api, "close", "TIME_SERIES_MONTHLY_ADJUSTED"
)
EOMONTH = Header.index_dates_to_end_of_month(API.set_index(API["timestamp"], drop=True))
EOMONTH = EOMONTH.replace(0, np.nan).bfill().ffill().fillna(1)
EOMONTH.to_csv("Collection Code Output/AV- FTSE 100 ME.csv")
del API

# %% 11. Large Cap RSI

os.chdir(r"C:\Users\jptth\Documents\GitHub Data")
API = Header.iterating_through_RSI(companies, tickers, premium_api)
API = API.bfill()
API = API.fillna("50")
API.to_csv("Collection Code Output/AV- FTSE 100 RSI.csv")
del API

# %% 12. Large Cap Shareholder Equities

# table created on FAME by filtering for stock data>FTSE indexes>FTSE 100, stock data>listed/unlisted>listed.
# I then added the columns financials and ratios>balance sheet>shareholder funds.
os.chdir(r"C:\Users\jptth\Documents\GitHub Data")
FTSE_SE_raw = pd.read_excel(
    "FTSE 100 SE.xlsx", sheet_name="Results", index_col="Company name"
)
FTSE_SE_raw.drop(["BT GROUP PLC"], inplace=True)
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
        "September 2024",
    ],
    axis=0,
    inplace=True,
)
number_month_df = Header.month_year_to_eomonth(month_df)
number_month_df = (
    number_month_df.replace(to_replace=["n.a.", "n.s."], value=np.nan)
    .bfill()
    .fillna("0")
)
number_month_df.add_prefix("SE- ", axis=1).to_csv(
    "Collection Code Output/FTSE 100 SE Clean.csv"
)
del (FTSE_SE_raw, clean_df, month_df, number_month_df)

# %% 13. Large Cap Profit

# table created on FAME by filtering for stock data>FTSE indexes>FTSE 100, stock data>listed/unlisted>listed.
# I then added the columns financials and ratios>balance sheet>profit and loss account.
os.chdir(r"C:\Users\jptth\Documents\GitHub Data")
FTSE_profit_raw = pd.read_excel(
    "FTSE 100 Profit.xlsx", sheet_name="Results", index_col="Company name"
)
FTSE_profit_raw.drop(["BT GROUP PLC"], inplace=True)
clean_df = Header.clean_profit_data(FTSE_profit_raw)
month_df = Header.financial_year_to_monthly(clean_df)
month_df.drop(
    [
        "March 2025",
        "February 2025",
        "January 2025",
        "December 2024",
        "November 2024",
        "October 2024",
        "September 2024",
    ],
    axis=0,
    inplace=True,
)
number_month_df = Header.month_year_to_eomonth(month_df)
number_month_df = (
    number_month_df.replace(to_replace=["n.a.", "n.s."], value=np.nan)
    .bfill()
    .fillna("0")
)
number_month_df.add_prefix("Profit- ", axis=1).to_csv(
    "Collection Code Output/FTSE 100 Profit Clean.csv"
)
del (FTSE_profit_raw, clean_df, month_df, number_month_df)

# %% 14. We calculate the beta from the stock price.

os.chdir(r"C:\Users\jptth\Documents\GitHub Data")
first_date = EOMONTH.index[-1]
Returns = pd.DataFrame(index=EOMONTH.index)
Beta = pd.DataFrame(index=EOMONTH.index)
Returns["Revenue- Total"] = EOMONTH.sum(axis=1)
first_total_price = Returns.at[first_date, "Revenue- Total"]
Returns["Beta- Total"] = (
    Returns["Revenue- Total"] - first_total_price
) / first_total_price
dates = pd.DataFrame(EOMONTH.index)
for i in EOMONTH.columns:
    first_price = EOMONTH.at[first_date, i]
    Returns[i] = (EOMONTH[i] - first_price) / first_price
for i in EOMONTH.columns:
    for a in dates[:-22].index:
        end_date = dates.at[a, "EOMONTH"]
        test_range = Returns[a : a + 23]
        if test_range[i].var() == 0:
            Beta.loc[end_date, "Beta- " + i] = 0
        else:
            Beta.loc[end_date, "Beta- " + i] = (
                test_range.cov().at["Beta- Total", i]
            ) / (test_range[i].var())
    for a in dates[-22:-1].index:
        end_date = dates.at[a, "EOMONTH"]
        test_range = Returns[a:]
        if test_range[i].var() == 0:
            Beta.loc[end_date, "Beta- " + i] = 0
        else:
            Beta.loc[end_date, "Beta- " + i] = (
                test_range.cov().at["Beta- Total", i]
            ) / (test_range[i].var())
    end_date = dates.at[len(dates) - 1, "EOMONTH"]
    Beta.loc[end_date, "Beta- " + i] = 0
Beta.to_csv("Collection Code Output/FTSE 100 Beta.csv")
del (EOMONTH, Beta, Returns, first_date, first_price, first_total_price, test_range)

# %% 15. Deleting the remaining variables. A sound signals the code is finished running.

del (companies, tickers, FTSE_df_raw)

import winsound

duration = 1000  # milliseconds
freq = 440  # Hz
winsound.Beep(freq, duration)
