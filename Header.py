import pandas as pd
import numpy as np
import os
import sys
from urllib.request import Request, urlopen
import json
import time
import calendar

# %% Libraries

monthly_df = pd.DataFrame(
    [
        ["January", 1],
        ["February", 2],
        ["March", 3],
        ["April", 4],
        ["May", 5],
        ["June", 6],
        ["July", 7],
        ["August", 8],
        ["September", 9],
        ["October", 10],
        ["November", 11],
        ["December", 12],
    ],
    columns=["Word", "Number"],
)
# %% <editor-fold desc="Data Collection & Cleaning">


def read_FAME_data(dataset_name, index=None):
    df = pd.read_excel(
        "Data/" + dataset_name + ".xlsx", sheet_name="Results", index_col=index
    )
    return df


def clean_ME_data(df_raw):
    """
    This function cleans the ME data from FAME and makes it into vertical variables by company
    :param df_raw: should be taken from the "results" sheet of the FAME extract, with the index_col set as "Unnamed: 0"
    :return: a pandas DataFrame with vertical variables for Market Equity by month
    """
    df_raw.drop(
        labels=[
            "Primary UK SIC (2007) code",
            "Latest accounts date",
            "Operating revenue (Turnover)\nth GBP Last avail. yr",
            "Number of employees\nLast avail. yr",
        ],
        axis="columns",
        inplace=True,
    )
    df_companies = df_raw["Company name"]
    # We aim to transform the data to ease later manipulation.
    df_transpose = df_raw.set_index(df_companies)
    df_transpose = df_transpose.drop(["Company name"], axis=1)
    df_transpose = df_transpose.transpose()
    df_transpose.reset_index(inplace=True)
    # The names come as standard being super long. We shorten these for ease of use.
    df_dates = pd.DataFrame(df_raw.columns)
    df_dates = df_dates.drop(0)
    df_dates = df_dates.rename(columns={0: "Dates"})
    df_dates = df_dates.reset_index()
    df_dates = df_dates["Dates"]

    df_dates = df_dates.replace(
        to_replace="Monthly - Market Capitalisation - ", value="", regex=True
    )
    df_dates = df_dates.replace(to_replace="\nth GBP", value="", regex=True)
    df_transpose["Dates"] = df_dates
    df_transpose = df_transpose.set_index("Dates")
    df_transpose = df_transpose.drop(labels=["index"], axis="columns")
    return df_transpose


def clean_SE_data(df_raw):
    """
    This function cleans the SE data from FAME and makes it into vertical variables by company
    :param df_raw: should be taken from the "results" sheet of the FAME extract, with the index_col set as "Company name"
    :return: a pandas DataFrame with vertical variables for Stockholder Equity by year
    """
    df_raw = df_raw.drop(
        labels=["Unnamed: 0", "Ticker symbol"],
        axis="columns",
    )
    df_transpose = df_raw.transpose()

    df_transpose.reset_index(inplace=True)
    # We remove the superfluous words from the index:
    df_dates = pd.DataFrame(df_raw.columns)
    #    df_dates.drop(0, inplace=True)
    df_dates.replace(
        to_replace=["Shareholders Funds", "\n", "th GBP ", "GBP "],
        value="",
        regex=True,
        inplace=True,
    )
    # And return the index to the DataFrame:
    df_dates.reset_index(inplace=True, drop=True)
    df_transpose["Years"] = df_dates
    df_transpose.set_index("Years", inplace=True)
    return df_transpose.drop("index", axis=1)


def clean_profit_data(df_raw):
    """
    This function cleans the profit data from FAME and makes it into vertical variables by company
    :param df_raw: should be taken from the "results" sheet of the FAME extract, with the index_col set as "Company name"
    :return: a pandas DataFrame with vertical variables for Profit margin % by year
    """
    df_raw = df_raw.drop(
        labels=["Unnamed: 0", "Ticker symbol"],
        axis="columns",
    )
    df_transpose = df_raw.transpose()

    df_transpose.reset_index(inplace=True)
    # We remove the superfluous words from the index:
    df_dates = pd.DataFrame(df_raw.columns)
    #    df_dates.drop(0, inplace=True)
    df_dates.replace(
        to_replace=[
            "Profit Margin",
            "\n",
        ],
        value="",
        regex=True,
        inplace=True,
    )
    # And return the index to the DataFrame:
    df_dates.reset_index(inplace=True, drop=True)
    df_transpose["Years"] = df_dates
    df_transpose.set_index("Years", inplace=True)
    return df_transpose.drop("index", axis=1)


def financial_year_to_monthly(df_raw):
    Years = pd.DataFrame(df_raw.index)
    Months = pd.DataFrame(
        [
            ["March ", 1],
            ["February ", 1],
            ["January ", 1],
            ["December ", 0],
            ["November ", 0],
            ["October ", 0],
            ["September ", 0],
            ["August ", 0],
            ["July ", 0],
            ["June ", 0],
            ["May ", 0],
            ["April ", 0],
        ]
    )
    number_of_years = len(Years)
    Dates = pd.DataFrame(index=range(12 * number_of_years), columns=["Dates", "Years"])
    for y in range(number_of_years):
        for i in range(12):
            Dates.loc[y * 12 + i, "Dates"] = Months.loc[i, 0] + str(
                int(Years.loc[y, "Years"]) + Months.loc[i, 1]
            )
            Dates.loc[y * 12 + i, "Years"] = Years.loc[y, "Years"]
    month_lookup = dict(zip(Dates.Dates, Dates.Years))
    new = Dates.set_index("Years").join(df_raw)
    new.set_index("Dates", inplace=True, drop=True)
    return new


def alphavantage_csv(function, company, apikey):
    url = (
        "https://www.alphavantage.co/query?function="
        + function
        + "&symbol="
        + company
        + "&apikey="
        + apikey
        + "&datatype=csv "
    )
    df = pd.read_csv(url)
    return df


def alphavantage_json(function, company, apikey):
    request = Request(
        "https://www.alphavantage.co/query?function="
        + function
        + "&symbol="
        + company
        + "&apikey="
        + apikey
        + "&datatype=csv"
    )
    response = urlopen(request)
    elevations = response.read()
    data = json.loads(elevations)
    return data


def sourcing_alphavantage_data(companies, company_tickers, apikey, kpi, function):
    """


    Parameters
    ----------
    companies : DataFrame of strings
        Desired companies' stock symbols
    kpi: String
        Desired column name
    apikey : String
        API key used to source data
    function : String
        for example "TIME_SERIES_MONTHLY_ADJUSTED"

    Returns df: a dataframe with all the requested companys' data.
    -------

    """
    # The first entry serves as an example:
    sample = alphavantage_csv(function, company_tickers.iloc[0], apikey)
    timestamp = sample["timestamp"]
    df = pd.DataFrame(timestamp, columns=["timestamp"])
    df[companies.iloc[0]] = sample[kpi]
    # With the parameters for the df defined, we can iterate through the remaining companies.
    for i in range(1, len(companies)):
        company_ticker = company_tickers.iloc[i]
        print(company_ticker + " - " + companies.iloc[i])
        time.sleep(0.75)
        dataset = alphavantage_csv(function, company_ticker, apikey)
        # Some stocks, AV has with the suffix ".L" or ".LON".
        if "Invalid API call" in dataset.iloc[0, 0]:
            dataset = alphavantage_csv(function, company_ticker + ".L", apikey)
        if kpi not in dataset.columns:
            print("FAIL")
            dataset.to_csv("test_API.csv")
            return df

        df[companies.iloc[i]] = dataset[kpi]
    return df


def alphavantage_RSI(company, apikey):
    request = Request(
        "https://www.alphavantage.co/query?function=RSI&symbol="
        + company
        + ".L&interval=monthly&time_period=6&series_type=close&apikey="
        + apikey
    )
    response = urlopen(request)
    elevations = response.read()
    data = json.loads(elevations)
    if not data:
        print("ERROR- Trying" + company)
        request = Request(
            "https://www.alphavantage.co/query?function=RSI&symbol="
            + company
            + "&interval=monthly&time_period=6&series_type=close&apikey="
            + apikey
        )
        response = urlopen(request)
        elevations = response.read()
        data = json.loads(elevations)
        if not data:
            print("ERROR even with .L")
            return pd.DataFrame()
    df = pd.json_normalize(data["Technical Analysis: RSI"])
    report = pd.DataFrame()
    report[company] = df.iloc[0]
    a = report.reset_index()["index"].str.split("-", expand=True)
    a = a.drop(2, axis=1).astype(int)
    a["EOMONTH"] = "ERROR"
    for A in range(len(a)):
        eomonth = (
            str(a.loc[A, 0])
            + "-"
            + str(a.loc[A, 1])
            + "-"
            + str(calendar.monthrange(a.loc[A, 0], a.loc[A, 1])[1])
        )
        a.iloc[A, 2] = eomonth
    return report.set_index(a["EOMONTH"], drop=True)


def iterating_through_RSI(companies, tickers, apikey):
    length = len(tickers)
    if len(companies) != length:
        print("INPUT ERROR")
        exit()
    df = alphavantage_RSI(tickers[0], apikey)
    for i in range(length):
        time.sleep(0.75)
        print(str(i) + ". " + tickers[i] + "- " + companies[i])
        api_output = alphavantage_RSI(tickers[i], apikey)
        df["RSI- " + companies[i]] = api_output
    return df.drop([tickers[0]], axis=1)


def index_dates_to_end_of_month(df_raw):
    df_index = pd.DataFrame()
    df_index["timestamp"] = df_raw.index
    df = df_index["timestamp"].str.split("-", expand=True)
    df = df.drop(2, axis=1).astype(int)
    df["EOMONTH"] = "ERROR"
    for J in range(len(df_index)):
        eomonth = (
            str(df.loc[J, 0])
            + "-"
            + str(df.loc[J, 1])
            + "-"
            + str(calendar.monthrange(df.loc[J, 0], df.loc[J, 1])[1])
        )
        df.iloc[J, 2] = eomonth
    df_new = df_raw.set_index(df["EOMONTH"], drop=True)
    return df_new.drop(["timestamp"], axis=1)


def month_year_to_eomonth(df_raw):
    df = df_raw.reset_index()["Dates"].str.split(" ", expand=True)
    monthly_df = pd.DataFrame(
        [
            ["January", 1],
            ["February", 2],
            ["March", 3],
            ["April", 4],
            ["May", 5],
            ["June", 6],
            ["July", 7],
            ["August", 8],
            ["September", 9],
            ["October", 10],
            ["November", 11],
            ["December", 12],
        ],
        columns=["Word", "Number"],
    )
    month_dict = dict(zip(monthly_df["Word"], monthly_df["Number"]))
    df["Month_Number"] = df[0].map(month_dict)
    df["EOMONTH"] = "ERROR"
    for J in range(len(df)):
        eomonth = (
            str(df.iloc[J, 1])
            + "-"
            + str(df.iloc[J, 2])
            + "-"
            + str(calendar.monthrange(int(df.iloc[J, 1]), int(df.iloc[J, 2]))[1])
        )
        df.iloc[J, 3] = eomonth
    return df_raw.set_index(df["EOMONTH"], drop=True)


# </editor-fold>

# %% <editor-fold desc="Regression Functions">


def normalise_df(df):
    df_float = df.astype(float)
    min_value = df_float.min().min()
    max_value = df_float.max().max()
    return (df_float - min_value).div(max_value - min_value)


def normalise_column(df, flt=False):
    if float == False:
        df_float = df.astype(float)
    else:
        df_float = df
    min_value = df_float.min()
    max_value = df_float.max()
    return (df_float - min_value).div(max_value - min_value)


def payoff_matrix(ME, hold_for, chosen_dates, perfect_information=True):
    if perfect_information == True:
        cost_adjustment = 0
        revenue_adjustment = -hold_for
    else:
        cost_adjustment = hold_for
        revenue_adjustment = 0
    Cost = ME.shift(cost_adjustment).loc[chosen_dates]
    Revenue = ME.shift(revenue_adjustment).loc[chosen_dates]
    Payoff = Revenue - Cost
    return Payoff


def company_dataset(
    company_name,
    dates,
    ME_clean,
    SE_clean,
    RSI_clean,
    Profit_clean,
    Beta_clean,
    hold_for,
):
    df = pd.DataFrame(index=dates["EOMONTH"])
    first_date = dates.reset_index().at[0, "EOMONTH"]
    first_stock_price = ME_clean.at[first_date, company_name]
    df["Returns"] = payoff_matrix(
        ME_clean, hold_for, df.index, perfect_information=False
    )[company_name]
    df["ME"] = ME_clean[company_name].shift(-hold_for).astype(float) - first_stock_price
    df["RSI"] = RSI_clean[company_name].shift(-hold_for)
    df["VAL"] = SE_clean[company_name].shift(-hold_for).div(ME_clean[company_name])
    df["GP"] = Profit_clean[company_name].shift(-hold_for)
    df["Beta"] = Beta_clean[company_name].shift(-hold_for)
    df["LAG"] = (
        ME_clean[company_name]
        .astype(float)
        .shift(-hold_for - 1, fill_value=ME_clean.at[first_date, company_name])
    )
    return df.drop("ME", axis=1)


def snapshot(date, companies, ME, SE, RSI, Profit, Beta):
    df = pd.DataFrame(
        index=companies["Company name"],
        columns=["ME", "RSI", "SE-To-Drop", "VAL", "GP", "Beta"],
    )
    df["ME"] = ME.loc[date]
    RSI_Copy = RSI
    RSI_Copy.columns = RSI_Copy.columns.str.replace("RSI- ", "")
    df["RSI"] = RSI_Copy.loc[date]
    SE_Copy = SE
    SE_Copy.columns = SE_Copy.columns.str.replace("SE- ", "")
    df["SE-To-Drop"] = SE_Copy.loc[date]
    df["VAL"] = normalise_column(df["SE-To-Drop"].div(df["ME"]))
    df.drop("SE-To-Drop", axis=1, inplace=True)
    Profit_Copy = Profit
    Profit_Copy.columns = Profit_Copy.columns.str.replace("Profit- ", "")
    df["GP"] = Profit_Copy.loc[date]
    Beta_Copy = Beta
    Beta_Copy.columns = Beta_Copy.columns.str.replace("Beta- ", "")
    df["Beta"] = Beta_Copy.loc[date]
    df["LAG"] = ME.shift(-1).loc[date]
    return df


def row_by_row_average(df):
    test = pd.DataFrame(index=df.index, columns=["test"])
    for i in df.index:
        test.at[i, "test"] = df.loc[i].mean()
    return test


def test():
    print("SUCCESS")


# <editor-fold>
