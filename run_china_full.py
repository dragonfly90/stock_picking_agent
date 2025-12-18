import akshare as ak
import yfinance as yf
import pandas as pd
from jinja2 import Environment, FileSystemLoader
import os
import time
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed

# Configuration
TEMPLATE_DIR = 'templates'
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
OUTPUT_FILE = 'china_full.html'
MIN_MARKET_CAP = 10000000000  # 10 Billion CNY
MIN_PE = 0
MAX_PE = 100

def get_csi_tickers():
    """Fetch CSI 300 and CSI 500 constituents and convert to yfinance format."""
    print("Fetching CSI 300 and CSI 500 constituents...")
    tickers = set()
    
    try:
        # CSI 300
        df_300 = ak.index_stock_cons(symbol="000300")
        for code in df_300['品种代码']:
            if code.startswith('6'):
                tickers.add(f"{code}.SS")
            else:
                tickers.add(f"{code}.SZ")
                
        # CSI 500
        df_500 = ak.index_stock_cons(symbol="000905")
        for code in df_500['品种代码']:
            if code.startswith('6'):
                tickers.add(f"{code}.SS")
            else:
                tickers.add(f"{code}.SZ")
                
        print(f"Found {len(tickers)} unique tickers from CSI 300 + CSI 500.")
        return list(tickers)
    except Exception as e:
        print(f"Error fetching CSI data: {e}")
        return []

from fetch_china_data import CHINA_STOCK_INFO

def fetch_stock_data(ticker):
    """Fetch data for a single stock using yfinance."""
    try:
        stock = yf.Ticker(ticker)
        info = stock.info
        
        # Extract metrics
        price = info.get('currentPrice') or info.get('previousClose')
        pe = info.get('trailingPE')
        pb = info.get('priceToBook')
        market_cap = info.get('marketCap')
        
        # Use translated name if available, otherwise use yfinance name
        name = CHINA_STOCK_INFO.get(ticker, {}).get('name', info.get('longName', ticker))
        
        # Calculate change percentage if possible
        prev_close = info.get('previousClose')
        change_pct = 0.0
        if price and prev_close:
            change_pct = ((price - prev_close) / prev_close) * 100
            
        return {
            'ticker': ticker,
            'name': name,
            'price': price,
            'change_pct': change_pct,
            'pe': pe,
            'pb': pb,
            'market_cap': market_cap
        }
    except Exception:
        return None

def run_china_full_analysis():
    print("Starting Full China Market Analysis (CSI 800)...")
    
    # 1. Get Tickers
    tickers = get_csi_tickers()
    if not tickers:
        print("No tickers found. Aborting.")
        return

    # 2. Fetch Data in Parallel
    print(f"Fetching data for {len(tickers)} stocks using yfinance (multithreaded)...")
    stocks_data = []
    
    start_time = time.time()
    with ThreadPoolExecutor(max_workers=20) as executor:
        future_to_ticker = {executor.submit(fetch_stock_data, ticker): ticker for ticker in tickers}
        
        completed = 0
        total = len(tickers)
        
        for future in as_completed(future_to_ticker):
            data = future.result()
            if data:
                stocks_data.append(data)
            
            completed += 1
            if completed % 50 == 0:
                print(f"Progress: {completed}/{total}...", end='\r')
                
    end_time = time.time()
    print(f"\nFetched data for {len(stocks_data)} stocks in {end_time - start_time:.2f} seconds.")

    # 3. Filter and Sort
    filtered_data = []
    for stock in stocks_data:
        mc = stock['market_cap']
        pe = stock['pe']
        
        if mc and pe and mc > MIN_MARKET_CAP and MIN_PE < pe < MAX_PE:
            filtered_data.append({
                'ticker': stock['ticker'],
                'name': stock['name'],
                'price': f"¥{stock['price']:.2f}" if stock['price'] else "N/A",
                'change_pct': f"{stock['change_pct']:.2f}%",
                'pe': f"{pe:.2f}",
                'pb': f"{stock['pb']:.2f}" if stock['pb'] else "N/A",
                'market_cap': f"¥{mc/1e9:.1f}B",
                'market_cap_val': mc # For sorting
            })
            
    # Sort by Market Cap descending
    filtered_data.sort(key=lambda x: x['market_cap_val'], reverse=True)
    
    print(f"Filtered down to {len(filtered_data)} stocks (Market Cap > 10B, 0 < PE < 100).")

    # 4. Generate HTML
    env = Environment(loader=FileSystemLoader(TEMPLATE_DIR))
    template = env.get_template('china_full.html')
    
    date_str = datetime.now().strftime("%Y-%m-%d %H:%M")
    output_path = os.path.join(BASE_DIR, OUTPUT_FILE)
    
    html_content = template.render(
        date=date_str,
        stocks=filtered_data,
        title="A股全市场精选 (CSI 800 Picks)",
        current_page=OUTPUT_FILE,
        total_count=len(filtered_data)
    )
    
    with open(output_path, 'w') as f:
        f.write(html_content)
    print(f"\nGenerated {output_path}")

if __name__ == "__main__":
    run_china_full_analysis()
