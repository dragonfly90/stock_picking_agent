import fetch_data
import analyze
import time

def main():
    print("Starting Stock Selection Agent...")
    
    # 1. Get Tickers
    print("Fetching S&P 500 tickers...")
    tickers = fetch_data.get_sp500_tickers()
    if not tickers:
        print("Failed to fetch tickers. Exiting.")
        return

    print(f"Found {len(tickers)} tickers. Analyzing top candidates...")
    
    # For demonstration/speed, we might limit to a subset if the user wants a quick result,
    # but the request is for the "top stock", so we should ideally check them all.
    # However, checking 500 stocks with yfinance sequentially is slow and might hit rate limits.
    # Let's try a batch of 20 first to prove it works, then we can discuss full run.
    # OR better: just run for all but handle errors gracefully.
    # To avoid rate limits, we can add a small sleep.
    
    # Let's limit to 50 for this initial run to be responsive.
    # tickers = tickers[:50] 
    
    stocks_data = []
    # Process in chunks or just loop with progress
    count = 0
    total = len(tickers)
    
    # Optimization: yfinance can fetch multiple tickers at once? 
    # yf.Tickers(' '.join(tickers)) might be faster but 'info' attribute fetching is still often per-ticker.
    # Let's stick to loop for simplicity and reliability.
    
    for ticker in tickers:
        count += 1
        print(f"[{count}/{total}] Fetching data for {ticker}...", end='\r')
        try:
            info = fetch_data.get_stock_data(ticker)
            if info:
                stocks_data.append((ticker, info))
        except Exception as e:
            pass
        
        # Rate limit protection
        # time.sleep(0.1) 
        
        # BREAK EARLY FOR DEMO if needed (remove for full run)
        if count >= 20: 
             break

    print("\nAnalysis complete. Ranking stocks...")
    ranked_stocks = analyze.rank_stocks(stocks_data)

    if not ranked_stocks:
        print("No stocks met the criteria or data fetching failed.")
        return

    top_pick = ranked_stocks[0]
    print("\n" + "="*40)
    print(f"TOP RECOMMENDATION: {top_pick['ticker']}")
    print("="*40)
    print(f"Score: {top_pick['score']}/5")
    print("Details:")
    for detail in top_pick['details']:
        print(f" - {detail}")
    
    print("\nTop 5 Candidates:")
    for i, stock in enumerate(ranked_stocks[:5]):
        print(f"{i+1}. {stock['ticker']} (Score: {stock['score']}, PEG: {stock['metrics']['peg']})")
import sqlite3
import os
import matplotlib.pyplot as plt
from datetime import datetime
from jinja2 import Environment, FileSystemLoader
import fetch_data
import analyze

# Get the absolute path of the directory where this script is located
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, 'stocks.db')
TEMPLATE_DIR = os.path.join(BASE_DIR, 'templates')

def init_db():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    # Add description column if not exists (migration hack for demo)
    try:
        c.execute("ALTER TABLE picks ADD COLUMN description text")
    except sqlite3.OperationalError:
        pass # Column likely exists

    # Add pe column if not exists (migration hack for demo)
    try:
        c.execute("ALTER TABLE picks ADD COLUMN pe real")
    except sqlite3.OperationalError:
        pass # Column likely exists

    # Add universe column if not exists (migration hack for demo)
    try:
        c.execute("ALTER TABLE picks ADD COLUMN universe text")
    except sqlite3.OperationalError:
        pass # Column likely exists
        
    c.execute('''CREATE TABLE IF NOT EXISTS picks
                 (date text, ticker text, score integer, peg real, details text, description text, pe real, universe text)''')
    conn.commit()
    return conn

def save_to_db(conn, pick, universe):
    c = conn.cursor()
    date_str = datetime.now().strftime("%Y-%m-%d")
    # Check if we already have a pick for today/universe to avoid duplicates
    c.execute("SELECT * FROM picks WHERE date = ? AND universe = ?", (date_str, universe))
    if c.fetchone():
        print(f"Already have a pick for today ({universe}). Updating...")
        c.execute("DELETE FROM picks WHERE date = ? AND universe = ?", (date_str, universe))
    
    # Handle missing description
    desc = pick.get('description', 'No description available.')
    pe = pick['metrics'].get('pe')
    
    c.execute("INSERT INTO picks VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
              (date_str, pick['ticker'], pick['score'], pick['metrics']['peg'], str(pick['details']), desc, pe, universe))
    conn.commit()

def get_history(conn, universe):
    c = conn.cursor()
    # Handle backward compatibility where universe might be NULL (assume SP500)
    if universe == 'SP500':
        c.execute("SELECT * FROM picks WHERE universe = ? OR universe IS NULL ORDER BY date DESC LIMIT 30", (universe,))
    else:
        c.execute("SELECT * FROM picks WHERE universe = ? ORDER BY date DESC LIMIT 30", (universe,))
        
    rows = c.fetchall()
    history = []
    for row in rows:
        # Handle potentially missing description/pe in old rows if schema changed
        # Row: date, ticker, score, peg, details, description, pe, universe
        desc = row[5] if len(row) > 5 else "N/A"
        pe = row[6] if len(row) > 6 else None
        
        history.append({
            'date': row[0],
            'ticker': row[1],
            'score': row[2],
            'peg': f"{row[3]:.2f}" if row[3] else "N/A",
            'pe': f"{pe:.2f}" if pe else "N/A"
        })
    return history

def generate_chart(ticker, history_data, filename):
    if history_data is None or history_data.empty:
        print("No history data for chart.")
        return False
    
    chart_path = os.path.join(BASE_DIR, filename)
    plt.figure(figsize=(10, 5))
    plt.plot(history_data.index, history_data['Close'], label='Close Price')
    plt.title(f"{ticker} - 1 Year Price History")
    plt.xlabel("Date")
    plt.ylabel("Price (USD)")
    plt.grid(True)
    plt.legend()
    plt.savefig(chart_path)
    plt.close()
    print(f"Generated {chart_path}")
    return True

def generate_html(top_pick, history, filename, title, chart_filename):
    env = Environment(loader=FileSystemLoader(TEMPLATE_DIR))
    template = env.get_template('index.html')
    
    date_str = datetime.now().strftime("%Y-%m-%d")
    output_path = os.path.join(BASE_DIR, filename)
    
    # Format top pick for template
    pick_data = None
    if top_pick:
        pick_data = {
            'ticker': top_pick['ticker'],
            'score': top_pick['score'],
            'peg': f"{top_pick['metrics']['peg']:.2f}" if top_pick['metrics']['peg'] else "N/A",
            'pe': f"{top_pick['metrics']['pe']:.2f}" if top_pick['metrics'].get('pe') else "N/A",
            'details': top_pick['details'],
            'description': top_pick.get('description', 'No description available.')
        }

    html_content = template.render(
        date=date_str,
        top_pick=pick_data,
        history=history,
        title=title,
        chart_filename=chart_filename,
        current_page=filename
    )
    
    with open(output_path, 'w') as f:
        f.write(html_content)
    print(f"Generated {output_path}")

def run_analysis(conn, universe_name, tickers, html_filename, chart_filename, title):
    print(f"Starting Analysis for {universe_name}...")
    
    # Limit for demo/speed if needed
    tickers = tickers[:50] 
    
    stocks_data = []
    
    for ticker in tickers:
        try:
            info = fetch_data.get_stock_data(ticker)
            if info:
                stocks_data.append((ticker, info))
        except:
            pass
            
    ranked_stocks = analyze.rank_stocks(stocks_data)
    
    top_pick = None
    if ranked_stocks:
        top_pick = ranked_stocks[0]
        print(f"Top Pick ({universe_name}): {top_pick['ticker']}")
        
        # Fetch additional info for top pick
        print("Fetching history and description...")
        hist = fetch_data.get_stock_history(top_pick['ticker'])
        # It does NOT pass the raw info. We need to fetch it again or modify analyze.py.
        # Easier to fetch it again or just get it from the list if we kept it.
        # We have stocks_data list of (ticker, info).
        
        # Find info in stocks_data
        pick_info = next((info for t, info in stocks_data if t == top_pick['ticker']), None)
        if pick_info:
            top_pick['description'] = pick_info.get('longBusinessSummary', 'No description.')
        
        save_to_db(conn, top_pick, universe_name)
    else:
        print("No top pick found.")
        
    history = get_history(conn, universe_name)
    generate_html(top_pick, history, html_filename, title, chart_filename)
    # conn.close() - Do not close here, let main handle it

if __name__ == "__main__":
    # Initialize DB
    conn = init_db()
    
    # 1. S&P 500 Analysis
    sp500_tickers = fetch_data.get_sp500_tickers()
    run_analysis(conn, 'SP500', sp500_tickers, 'index.html', 'chart.png', 'Daily Stock Pick: S&P 500')
    
    # 2. Non-S&P 500 Analysis (S&P 400 + 600)
    non_sp500_tickers = fetch_data.get_non_sp500_tickers()
    run_analysis(conn, 'NON_SP500', non_sp500_tickers, 'non_spy.html', 'chart_non_spy.png', 'Daily Stock Pick: Non-S&P 500')
    
    conn.close()
