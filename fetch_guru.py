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

def get_cash_history(ticker="BRK-B"):
    """
    Fetches historical cash allocation percentage (Cash + Short Term Inv / Total Assets).
    Returns a list of dictionaries: [{'date': date, 'cash_pct': pct}, ...]
    """
    if not ticker:
        return []
        
    try:
        print(f"Fetching cash history for {ticker}...")
        stock = yf.Ticker(ticker)
        bs = stock.quarterly_balance_sheet
        
        history = []
        
        # Iterate through columns (dates)
        for date in bs.columns:
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
                history.append({
                    'date': date,
                    'cash_pct': pct,
                    'cash_val': cash,
                    'total_assets': total_assets
                })
        
        # Sort by date ascending
        history.sort(key=lambda x: x['date'])
        return history
        
    except Exception as e:
        print(f"Error fetching cash history for {ticker}: {e}")
        return []


if __name__ == "__main__":
    # Test
    holdings = get_dataroma_holdings()
    print(f"Found {len(holdings)} holdings.")
    if holdings:
        print(f"Top holding: {holdings[0]}")
        
    cash = get_cash_position()
    print(f"Cash: ${cash:,.2f}")
