import yfinance as yf
import pandas as pd
import requests
from bs4 import BeautifulSoup

def get_sp500_tickers():
    """Scrapes the list of S&P 500 tickers from Wikipedia."""
    url = "https://en.wikipedia.org/wiki/List_of_S%26P_500_companies"
    headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.114 Safari/537.36'}
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
        table = soup.find('table', {'id': 'constituents'})
        tickers = []
        for row in table.findAll('tr')[1:]:
            ticker = row.findAll('td')[0].text.strip()
            tickers.append(ticker)
        return tickers
    except Exception as e:
        print(f"Error fetching S&P 500 tickers: {e}")
        return []

def get_stock_data(ticker):
    """Fetches financial data for a given ticker using yfinance."""
    try:
        stock = yf.Ticker(ticker)
        # We need info for valuation and growth metrics
        info = stock.info
        return info
    except Exception as e:
        print(f"Error fetching data for {ticker}: {e}")
        return None

def get_stock_history(ticker):
    """Fetches 1 year of historical data for a ticker."""
    try:
        stock = yf.Ticker(ticker)
        # Fetch 1 year of history
        hist = stock.history(period="1y")
        return hist
    except Exception as e:
        print(f"Error fetching history for {ticker}: {e}")
        return None

if __name__ == "__main__":
    # Test the functions
    tickers = get_sp500_tickers()
    print(f"Found {len(tickers)} tickers.")
    if tickers:
        print(f"Sample ticker: {tickers[0]}")
        data = get_stock_data(tickers[0])
        if data:
            print(f"Sample data keys: {list(data.keys())[:5]}")
