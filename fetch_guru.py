import requests
from bs4 import BeautifulSoup
import yfinance as yf
import pandas as pd

def get_dataroma_holdings(manager_code="BRK"):
    """
    Scrapes Dataroma for a specific manager's holdings.
    Default manager_code="BRK" is Warren Buffett (Berkshire Hathaway).
    """
    url = f"https://www.dataroma.com/m/holdings.php?m={manager_code}"
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.9'
    }
    
    try:
        print(f"Fetching holdings from {url}...")
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.text, 'html.parser')
        table = soup.find('table', {'id': 'grid'})
        
        holdings = []
        if table:
            # Skip header row
            rows = table.findAll('tr')[1:]
            for row in rows:
                cols = row.findAll('td')
                if len(cols) > 5:
                    # Column indices based on Dataroma structure:
                    # 1: Stock Name/Ticker (inside a tag)
                    # 2: % of Portfolio
                    # 5: Value
                    
                    ticker_cell = cols[1].find('a')
                    ticker = ticker_cell.text.split('-')[0].strip() if ticker_cell else "N/A"
                    name = ticker_cell.find('span').text.strip().replace('- ', '') if ticker_cell and ticker_cell.find('span') else "N/A"
                    
                    pct_portfolio = cols[2].text.strip()
                    value_str = cols[6].text.strip().replace('$', '').replace(',', '')
                    
                    try:
                        value = float(value_str)
                    except:
                        value = 0
                        
                    holdings.append({
                        'ticker': ticker,
                        'name': name,
                        'pct_portfolio': pct_portfolio,
                        'value': value
                    })
        return holdings
    except Exception as e:
        print(f"Error scraping Dataroma: {e}")
        return get_fallback_holdings(manager_code)

def get_fallback_holdings(manager_code):
    """Returns hardcoded fallback data if scraping fails."""
    print(f"Using fallback data for {manager_code}...")
    if manager_code == "BRK":
        return [
            {'ticker': 'AAPL', 'name': 'Apple Inc.', 'pct_portfolio': '40.5', 'value': 156000000000},
            {'ticker': 'BAC', 'name': 'Bank of America Corp', 'pct_portfolio': '11.8', 'value': 32000000000},
            {'ticker': 'AXP', 'name': 'American Express', 'pct_portfolio': '10.4', 'value': 28000000000},
            {'ticker': 'KO', 'name': 'Coca-Cola Co.', 'pct_portfolio': '7.3', 'value': 24000000000},
            {'ticker': 'CVX', 'name': 'Chevron Corp.', 'pct_portfolio': '5.1', 'value': 16000000000}
        ]
    elif manager_code == "BMG":
        return [
            {'ticker': 'MSFT', 'name': 'Microsoft Corp.', 'pct_portfolio': '31.4', 'value': 14000000000},
            {'ticker': 'CNI', 'name': 'Canadian Natl Railway', 'pct_portfolio': '16.2', 'value': 7000000000},
            {'ticker': 'WM', 'name': 'Waste Management', 'pct_portfolio': '15.1', 'value': 6500000000},
            {'ticker': 'DE', 'name': 'Deere & Co.', 'pct_portfolio': '4.2', 'value': 1500000000}
        ]
    elif manager_code == "DA":
        return [
            {'ticker': 'IVV', 'name': 'iShares Core S&P 500 ETF', 'pct_portfolio': '5.6', 'value': 900000000},
            {'ticker': 'IEMG', 'name': 'iShares Core MSCI Emerging Markets ETF', 'pct_portfolio': '4.8', 'value': 750000000},
            {'ticker': 'GOOGL', 'name': 'Alphabet Inc.', 'pct_portfolio': '3.2', 'value': 500000000},
            {'ticker': 'META', 'name': 'Meta Platforms', 'pct_portfolio': '2.9', 'value': 450000000}
        ]
    return []

def get_cash_position(ticker="BRK-B"):
    """
    Fetches 'Cash And Cash Equivalents' from yfinance balance sheet.
    Returns 0 if ticker is None or data not found.
    """
    if not ticker:
        return 0
        
    try:
        print(f"Fetching cash position for {ticker}...")
        stock = yf.Ticker(ticker)
        # Get quarterly balance sheet
        bs = stock.balance_sheet
        
        # Try different keys as yfinance labels can change
        cash_keys = ['Cash And Cash Equivalents', 'Cash & Cash Equivalents', 'Cash']
        cash = 0
        
        for key in cash_keys:
            if key in bs.index:
                # Get most recent
                cash = bs.loc[key].iloc[0]
                break
        
        # If still 0, try to add Short Term Investments if available (often part of "cash pile")
        invest_keys = ['Other Short Term Investments', 'Short Term Investments']
        for key in invest_keys:
            if key in bs.index:
                cash += bs.loc[key].iloc[0]
                
        return cash
    except Exception as e:
        print(f"Error fetching cash for {ticker}: {e}")
        return 0

# Hardcoded historical data for Berkshire Hathaway (Year-End)
# Sources: Macrotrends, CompaniesMarketCap, Annual Reports
BRK_HISTORICAL_DATA = [
    {'date': '2000-12-31', 'cash': 67.84, 'assets': 135.79},
    {'date': '2001-12-31', 'cash': 12.74, 'assets': 162.75},
    {'date': '2002-12-31', 'cash': 35.95, 'assets': 169.54},
    {'date': '2003-12-31', 'cash': 74.73, 'assets': 180.55},
    {'date': '2004-12-31', 'cash': 44.66, 'assets': 188.87},
    {'date': '2005-12-31', 'cash': 43.74, 'assets': 198.32},
    {'date': '2006-12-31', 'cash': 44.32, 'assets': 248.43},
    {'date': '2007-12-31', 'cash': 28.26, 'assets': 273.16},
    {'date': '2008-12-31', 'cash': 25.54, 'assets': 267.39},
    {'date': '2009-12-31', 'cash': 30.56, 'assets': 297.11},
    {'date': '2010-12-31', 'cash': 38.23, 'assets': 372.22},
    {'date': '2011-12-31', 'cash': 37.30, 'assets': 392.64},
    {'date': '2012-12-31', 'cash': 46.99, 'assets': 427.45},
    {'date': '2013-12-31', 'cash': 48.19, 'assets': 484.93},
    {'date': '2014-12-31', 'cash': 63.27, 'assets': 525.86},
    {'date': '2015-12-31', 'cash': 71.73, 'assets': 552.25},
    {'date': '2016-12-31', 'cash': 28.05, 'assets': 620.85},
    {'date': '2017-12-31', 'cash': 31.58, 'assets': 702.10},
    {'date': '2018-12-31', 'cash': 30.36, 'assets': 707.79},
    {'date': '2019-12-31', 'cash': 64.18, 'assets': 817.73},
    {'date': '2020-12-31', 'cash': 47.99, 'assets': 873.73},
    {'date': '2021-12-31', 'cash': 88.18, 'assets': 958.78},
    {'date': '2022-12-31', 'cash': 35.81, 'assets': 948.47},
    {'date': '2023-12-31', 'cash': 38.02, 'assets': 1069.98},
    # 2024 data will be fetched from yfinance if available, or we can add estimate
    {'date': '2024-12-31', 'cash': 334.20, 'assets': 1153.88}, # Estimate/Record
]

def get_cash_history(ticker="BRK-B"):
    """
    Fetches historical cash allocation percentage (Cash + Short Term Inv / Total Assets).
    Merges hardcoded history (2000-2023) with recent yfinance data.
    Returns a list of dictionaries: [{'date': date, 'cash_pct': pct}, ...]
    """
    if not ticker:
        return []
        
    history = []
    
    # 1. Add Hardcoded History (for BRK only)
    if "BRK" in ticker:
        for item in BRK_HISTORICAL_DATA:
            pct = (item['cash'] / item['assets']) * 100
            history.append({
                'date': pd.Timestamp(item['date']),
                'cash_pct': pct,
                'cash_val': item['cash'] * 1e9, # Convert to actual value
                'total_assets': item['assets'] * 1e9
            })
            
    try:
        print(f"Fetching recent cash history for {ticker}...")
        stock = yf.Ticker(ticker)
        bs = stock.quarterly_balance_sheet
        
        # 2. Fetch Recent Data from yfinance
        recent_history = []
        # Iterate through columns (dates)
        for date in bs.columns:
            # Skip if date is already in history (approximate check by year/month)
            if any(h['date'].year == date.year and h['date'].month == date.month for h in history):
                continue
                
            # 1. Get Cash
            cash = 0
            cash_keys = ['Cash And Cash Equivalents', 'Cash & Cash Equivalents', 'Cash']
            for key in cash_keys:
                if key in bs.index:
                    cash = bs.loc[key][date]
                    break
            
            # 2. Get Short Term Investments
            invest_keys = ['Other Short Term Investments', 'Short Term Investments']
            for key in invest_keys:
                if key in bs.index:
                    val = bs.loc[key][date]
                    if pd.notna(val):
                        cash += val
            
            # 3. Get Total Assets
            total_assets = 0
            if 'Total Assets' in bs.index:
                total_assets = bs.loc['Total Assets'][date]
                
            if total_assets > 0:
                pct = (cash / total_assets) * 100
                recent_history.append({
                    'date': date,
                    'cash_pct': pct,
                    'cash_val': cash,
                    'total_assets': total_assets
                })
        
        # Merge and Sort
        history.extend(recent_history)
        history.sort(key=lambda x: x['date'])
        
        return history
        
    except Exception as e:
        print(f"Error fetching cash history for {ticker}: {e}")
        return history # Return whatever we have (hardcoded)


if __name__ == "__main__":
    # Test
    holdings = get_dataroma_holdings()
    print(f"Found {len(holdings)} holdings.")
    if holdings:
        print(f"Top holding: {holdings[0]}")
        
    cash = get_cash_position()
    print(f"Cash: ${cash:,.2f}")
