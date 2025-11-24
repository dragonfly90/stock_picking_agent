import yfinance as yf
import json

def debug_ticker(ticker):
    stock = yf.Ticker(ticker)
    info = stock.info
    print(f"--- {ticker} ---")
    keys_of_interest = ['pegRatio', 'trailingPE', 'forwardPE', 'revenueGrowth', 'earningsGrowth', 'returnOnEquity', 'debtToEquity']
    for k in keys_of_interest:
        print(f"{k}: {info.get(k)}")

if __name__ == "__main__":
    debug_ticker("GOOGL")
