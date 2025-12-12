import yfinance as yf
import pandas as pd

ticker = "BRK-B"
stock = yf.Ticker(ticker)

print("--- Quarterly Short Term Investments ---")
keys = ['Other Short Term Investments', 'Short Term Investments']
for key in keys:
    if key in stock.quarterly_balance_sheet.index:
        print(f"{key}:")
        print(stock.quarterly_balance_sheet.loc[key])
