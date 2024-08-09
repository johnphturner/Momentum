This machine will assess the significance of factors, and use this to inform purchases and sales of shares.

Header.py contains the functions needed for the other codes to work.

Data_collection collects data and cleans it, ready for the main function. HOWEVER, the raw data must first be manually collected:
* For ticker information, I used https://fame-r1.bvdinfo.com . I saved this as 'FTSE SmallCap Tickers.xlsx' and 'FTSE 100 Tickers.xlsx'
* For Shareholder funds, I used https://fame-r1.bvdinfo.com . I saved this as 'FTSE Small Cap SE.xlsx' and 'FTSE 100 SE.xlsx'
* This should be all thats needed, but this code does assume access to a premium AlphaVantage API. This can be purchased here: https://www.alphavantage.co/premium/  , or the codes could be slowed to allow for a free key, found here: https://www.alphavantage.co/support/#api-key .
  
MAIN.py is the executable body of the machine. For this to work, the Data_collection codes must first be ran.
