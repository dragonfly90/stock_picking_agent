import yfinance as yf
import pandas as pd

ticker = "BRK-B"
stock = yf.Ticker(ticker)

print("--- Annual Balance Sheet ---")
print(stock.balance_sheet.loc[['Cash And Cash Equivalents', 'Total Assets']] if 'Total Assets' in stock.balance_sheet.index else "Keys not found")

print("\n--- Quarterly Balance Sheet ---")
print(stock.quarterly_balance_sheet.loc[['Cash And Cash Equivalents', 'Total Assets']] if 'Total Assets' in stock.quarterly_balance_sheet.index else "Keys not found")
