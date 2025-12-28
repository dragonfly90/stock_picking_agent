import yfinance as yf
import pandas as pd

def test_history():
    ticker = "BRK-B"
    print(f"Fetching history for {ticker}...")
    stock = yf.Ticker(ticker)
    
    # Try yearly
    print("\nYearly Balance Sheet:")
    bs_yearly = stock.balance_sheet
    print(bs_yearly.columns)
    
    # Try quarterly
    print("\nQuarterly Balance Sheet:")
    bs_quarterly = stock.quarterly_balance_sheet
    print(bs_quarterly.columns)

if __name__ == "__main__":
    test_history()
