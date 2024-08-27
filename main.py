# %% 1. First, let's import the necessary packages.

import pandas as pd
import numpy as np
import os

os.chdir(r"C:\Users\jptth\Documents\GitHub\Momentum")
filepath = os.getcwd()
import Header
from sklearn import linear_model as skl
import matplotlib.pyplot as plt

premium_api = "8NIR58ZCJWT4MFNH"
# This number is how long we hold the stock for
hold_for = int(input("How long should we hold for? integer prompt please: "))

# %% 2a. Run this cell for the Data. You will be prompted for which data you want to use:
os.chdir(filepath)
os.chdir("../../GitHub Data")
size = input('Type "Large" to run the FTSE 100, and "Small" to run the FTSE SmallCap: ')
while size not in ["Large", "Small"]:
    size = input('ERROR: input "Large" or "Small": ')
# This data comes from the Data_collection code.
# the double "%" is a Spyder feature, that separates code into executable cells.
if size == "Small":
    SE_clean = pd.read_csv(
        "Collection Code Output/FTSE SmallCap SE Clean.csv", index_col="EOMONTH"
    )
    RSI_clean = pd.read_csv(
        "Collection Code Output/AV- FTSE SmallCap RSI.csv", index_col="EOMONTH"
    )
    ME_clean = pd.read_csv(
        "Collection Code Output/AV- FTSE SmallCap ME.csv", index_col="EOMONTH"
    )
    Profit_clean = pd.read_csv(
        "Collection Code Output/FTSE SmallCap Profit Clean.csv", index_col="EOMONTH"
    )
    Beta_clean = pd.read_csv(
        "Collection Code Output/FTSE SmallCap Beta.csv", index_col="EOMONTH"
    )
else:
    SE_clean = pd.read_csv(
        "Collection Code Output/FTSE 100 SE Clean.csv", index_col="EOMONTH"
    )
    RSI_clean = pd.read_csv(
        "Collection Code Output/AV- FTSE 100 RSI.csv", index_col="EOMONTH"
    )
    ME_clean = pd.read_csv(
        "Collection Code Output/AV- FTSE 100 ME.csv", index_col="EOMONTH"
    )
    Profit_clean = pd.read_csv(
        "Collection Code Output/FTSE 100 Profit Clean.csv", index_col="EOMONTH"
    )
    Beta_clean = pd.read_csv(
        "Collection Code Output/FTSE 100 Beta.csv", index_col="EOMONTH"
    )

# %% 3. We can get a list of companies by taking the columns from one of these and cleaning:
Companies = pd.DataFrame(ME_clean.columns, columns=["Company name"])
# We only use dates that are in all of our datasets.
SE_Dates = pd.DataFrame(SE_clean.index)
RSI_Dates = pd.DataFrame(RSI_clean.index)
ME_Dates = pd.DataFrame(ME_clean.index)
Profit_Dates = pd.DataFrame(Profit_clean.index)
Beta_Dates = pd.DataFrame(Beta_clean.index)
Dates = pd.merge(SE_Dates, RSI_Dates, how="inner", on=["EOMONTH"])
Dates = pd.merge(Dates, ME_Dates, how="inner", on=["EOMONTH"])
Dates = Dates.reindex(index=Dates.index[::-1]).reset_index(drop=True)
del (SE_Dates, RSI_Dates, ME_Dates, Profit_Dates, Beta_Dates)

# %% 4. We aim to construct a for loop, across a range of dates.
# For each date, the code will create a regression model of the previous 2 years, to determine which factors are significant.
# For our loop, we drop the first 23 dates. This is because each regression model will work on the last 2 years.
Executable_Dates = Dates[23 + hold_for : -hold_for]

# We make the payoff matrix:
# First we reorder.
ME_ordered = ME_clean.loc[Dates["EOMONTH"].loc[hold_for:]]
# Now, we make a matrix shifted n-dates into the future, for the returns.
ME_shifted = ME_ordered.shift(-hold_for)
# This gives us a payoff matrix:
stock_movement = ME_shifted - ME_ordered
# But we need to divide through by the initial stock price, so it's just a $1 bet.
Payoff = stock_movement.div(ME_ordered)
del (ME_ordered, ME_shifted, stock_movement)


# We define these DataFrames outside of the loop, so they can be filled iteratively.
Coefficient_timeline = pd.DataFrame(
    columns=["RSI", "VAL", "GP", "Beta", "LAG"], index=Executable_Dates["EOMONTH"]
)
Dataset = pd.DataFrame()
Purchases = pd.DataFrame(
    columns=["1st Choice", "2nd Choice", "3rd Choice"],
    index=Executable_Dates["EOMONTH"],
)
PL = pd.DataFrame(
    columns=["1st Choice", "2nd Choice", "3rd Choice"],
    index=Executable_Dates["EOMONTH"],
)

for a in Executable_Dates.index:
    print(str(a) + "- " + Executable_Dates.at[a, "EOMONTH"])
    end_date = Executable_Dates.at[a, "EOMONTH"]
    chosen_dates = Dates[a - 23 : a + 1]
    snapshot = Header.snapshot(
        end_date, Companies, ME_clean, SE_clean, RSI_clean, Profit_clean, Beta_clean
    )
    for company_name in Companies["Company name"]:
        Company_df = Header.company_dataset(
            company_name,
            chosen_dates,
            ME_clean,
            SE_clean,
            RSI_clean,
            Profit_clean,
            Beta_clean,
            hold_for,
        )
        Company_df = Company_df.add_prefix(company_name + " ", axis=0)
        Dataset = pd.concat([Dataset, Company_df])
    reg = skl.Lasso(alpha=0.1)
    Dataset["VAL"] = Header.normalise_column(Dataset["VAL"], flt=True)
    x = Dataset[["RSI", "VAL", "GP", "Beta", "LAG"]]
    y = Dataset["Returns"]
    reg.fit(x, y)
    coefficients = reg.coef_
    Coefficient_timeline.loc[end_date] = coefficients
    snapshot["PME"] = (
        reg.intercept_
        + coefficients[0] * snapshot["RSI"]
        + coefficients[1] * snapshot["VAL"]
        + coefficients[2] * snapshot["GP"]
        + coefficients[3] * snapshot["Beta"]
        + coefficients[4] * snapshot["LAG"]
    )
    snapshot["Rank"] = len(snapshot) + 1 - snapshot["PME"].rank()
    snapshot["Companies"] = snapshot.index
    Purchases.at[end_date, "1st Choice"] = snapshot.set_index("Rank").at[1, "Companies"]
    Purchases.at[end_date, "2nd Choice"] = snapshot.set_index("Rank").at[2, "Companies"]
    Purchases.at[end_date, "3rd Choice"] = snapshot.set_index("Rank").at[3, "Companies"]
    PL.at[end_date, "1st Choice"] = Payoff.at[
        end_date, Purchases.at[end_date, "1st Choice"]
    ]
    PL.at[end_date, "2nd Choice"] = Payoff.at[
        end_date, Purchases.at[end_date, "2nd Choice"]
    ]
    PL.at[end_date, "3rd Choice"] = Payoff.at[
        end_date, Purchases.at[end_date, "3rd Choice"]
    ]

# %% 5. We analyse the results with a graph, and export.

os.chdir(filepath)
os.chdir("../../GitHub Data")
PL["Total"] = PL["1st Choice"] + PL["2nd Choice"] + PL["3rd Choice"]
PL["CumSum"] = PL["Total"].cumsum()

comparison = pd.DataFrame()
average = Header.row_by_row_average(Payoff).loc[Executable_Dates["EOMONTH"]]
comparison["index"] = (3 * average["test"]).cumsum()
comparison["portfolio"] = PL["CumSum"]

plt.plot(Executable_Dates["EOMONTH"], comparison["index"], label="Index")
plt.plot(Executable_Dates["EOMONTH"], comparison["portfolio"], label="Portfolio")

plt.xlabel("Months")
plt.ylabel("P&L")
plt.title("Returns vs Index Portfolio")
plt.legend()
plt.show()

Purchases.to_csv(
    "Results/" + size + "Cap holding for " + str(hold_for) + " mths- purchases.csv"
)
comparison.to_csv(
    "Results/" + size + "Cap holding for " + str(hold_for) + " mths- performance.csv"
)
Coefficient_timeline.to_csv(
    "Results/" + size + "Cap holding for " + str(hold_for) + " mths- Coefficients.csv"
)
