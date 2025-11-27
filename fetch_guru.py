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
        return []

def get_cash_position(ticker="BRK-B"):
    """
    Fetches 'Cash And Cash Equivalents' from yfinance balance sheet.
    """
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

if __name__ == "__main__":
    # Test
    holdings = get_dataroma_holdings()
    print(f"Found {len(holdings)} holdings.")
    if holdings:
        print(f"Top holding: {holdings[0]}")
        
    cash = get_cash_position()
    print(f"Cash: ${cash:,.2f}")
