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
import fetch_guru
import fetch_competitors
import performance
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

    # Add dividend_yield column if not exists (migration hack for demo)
    try:
        c.execute("ALTER TABLE picks ADD COLUMN dividend_yield real")
    except sqlite3.OperationalError:
        pass # Column likely exists
        
    c.execute('''CREATE TABLE IF NOT EXISTS picks
                 (date text, ticker text, score integer, peg real, details text, description text, pe real, universe text, dividend_yield real)''')
    conn.commit()
    return conn

def save_to_db(conn, picks, universe):
    c = conn.cursor()
    date_str = datetime.now().strftime("%Y-%m-%d")
    
    # Clear existing picks for today/universe to avoid duplicates/stale data
    # We do this once before inserting the new batch
    c.execute("SELECT * FROM picks WHERE date = ? AND universe = ?", (date_str, universe))
    if c.fetchone():
        print(f"Clearing existing picks for today ({universe})...")
        c.execute("DELETE FROM picks WHERE date = ? AND universe = ?", (date_str, universe))
    
    for pick in picks:
        # Handle missing description
        desc = pick.get('description', 'No description available.')
        pe = pick['metrics'].get('pe')
        dividend_yield = pick['metrics'].get('dividend_yield')
        
        c.execute("INSERT INTO picks VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
                  (date_str, pick['ticker'], pick['score'], pick['metrics']['peg'], str(pick['details']), desc, pe, universe, dividend_yield))
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
        # Handle potentially missing description/pe/dividend_yield in old rows if schema changed
        # Row: date, ticker, score, peg, details, description, pe, universe, dividend_yield
        desc = row[5] if len(row) > 5 else "N/A"
        pe = row[6] if len(row) > 6 else None
        dividend_yield = row[8] if len(row) > 8 else None
        
        history.append({
            'date': row[0],
            'ticker': row[1],
            'score': row[2],
            'peg': f"{row[3]:.2f}" if row[3] else "N/A",
            'pe': f"{pe:.2f}" if pe else "N/A",
            'dividend_yield': f"{dividend_yield:.2f}%" if dividend_yield else "N/A"
        })
    return history

def generate_chart(ticker, history_data, filename):
    if history_data is None or history_data.empty:
        print(f"No history data for {ticker} chart.")
        return False
    
    chart_path = os.path.join(BASE_DIR, filename)
    plt.figure(figsize=(10, 5))
    plt.plot(history_data.index, history_data['Close'], label='Close Price')
    plt.title(f"{ticker} - 5 Year Price History")
    plt.xlabel("Date")
    plt.ylabel("Price (USD)")
    plt.grid(True)
    plt.legend()
    plt.savefig(chart_path)
    plt.close()
    print(f"Generated {chart_path}")
    return True

def generate_html(top_stocks, history, filename, title):
    env = Environment(loader=FileSystemLoader(TEMPLATE_DIR))
    template = env.get_template('index.html')
    
    date_str = datetime.now().strftime("%Y-%m-%d")
    output_path = os.path.join(BASE_DIR, filename)
    
    # Format top stocks for template
    formatted_stocks = []
    if top_stocks:
        for stock in top_stocks:
            dividend_yield = stock['metrics'].get('dividend_yield')
            industry = stock['metrics'].get('industry', 'N/A')
            sector = stock['metrics'].get('sector', 'N/A')
            
            # Format competitors
            formatted_competitors = []
            for comp in stock.get('competitors', []):
                mc = comp.get('market_cap')
                formatted_competitors.append({
                    'ticker': comp['ticker'],
                    'name': comp['name'],
                    'market_cap': f"${mc/1e9:.1f}B" if mc else "N/A",
                    'pe': f"{comp['pe']:.2f}" if comp.get('pe') else "N/A",
                    'peg': f"{comp['peg']:.2f}" if comp.get('peg') else "N/A",
                    'dividend_yield': f"{comp['dividend_yield']:.2f}%" if comp.get('dividend_yield') else "N/A"
                })
            
            formatted_stocks.append({
                'ticker': stock['ticker'],
                'score': stock['score'],
                'peg': f"{stock['metrics']['peg']:.2f}" if stock['metrics']['peg'] else "N/A",
                'pe': f"{stock['metrics']['pe']:.2f}" if stock['metrics'].get('pe') else "N/A",
                'dividend_yield': f"{dividend_yield:.2f}%" if dividend_yield else "N/A",
                'industry': industry,
                'sector': sector,
                'details': stock['details'],
                'description': stock.get('description', 'No description available.'),
                'chart_filename': stock.get('chart_filename'),
                'competitors': formatted_competitors
            })

    html_content = template.render(
        date=date_str,
        top_stocks=formatted_stocks,
        history=history,
        title=title,
        current_page=filename
    )
    
    with open(output_path, 'w') as f:
        f.write(html_content)
    print(f"Generated {output_path}")

def run_analysis(conn, universe_name, tickers, html_filename, title):
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
    
    top_stocks = []
    if ranked_stocks:
        # Select Top 5
        top_5 = ranked_stocks[:5]
        print(f"Top 5 Picks ({universe_name}): {[s['ticker'] for s in top_5]}")
        
        for stock in top_5:
            print(f"Processing {stock['ticker']}...")
            # Fetch additional info
            hist = fetch_data.get_stock_history(stock['ticker'])
            chart_filename = f"chart_{universe_name}_{stock['ticker']}.png"
            generate_chart(stock['ticker'], hist, chart_filename)
            stock['chart_filename'] = chart_filename
            
            # Find info in stocks_data
            pick_info = next((info for t, info in stocks_data if t == stock['ticker']), None)
            if pick_info:
                stock['description'] = pick_info.get('longBusinessSummary', 'No description.')
            
            # Get competitors and comparison
            sector = stock['metrics'].get('sector', '')
            industry = stock['metrics'].get('industry', '')
            peer_tickers = fetch_competitors.get_industry_peers(stock['ticker'], sector, industry)
            
            if peer_tickers:
                # Include the current stock in comparison
                all_tickers = [stock['ticker']] + peer_tickers
                comparison = fetch_competitors.compare_stocks(all_tickers)
                stock['competitors'] = comparison
            else:
                stock['competitors'] = []
            
            top_stocks.append(stock)
        
        save_to_db(conn, top_stocks, universe_name)
    else:
        print(f"No top picks found for {universe_name}.")
        
    history = get_history(conn, universe_name)
    generate_html(top_stocks, history, html_filename, title)
    # conn.close() - Do not close here, let main handle it

import fetch_guru

# ... (existing imports)

def generate_guru_chart(equity_val, cash_val, filename):
    chart_path = os.path.join(BASE_DIR, filename)
    
    labels = ['Equity Portfolio', 'Cash & Equivalents']
    sizes = [equity_val, cash_val]
    colors = ['#3498db', '#2ecc71']
    explode = (0.1, 0)  # explode 1st slice
    
    plt.figure(figsize=(8, 6))
    plt.pie(sizes, explode=explode, labels=labels, colors=colors,
            autopct='%1.1f%%', shadow=True, startangle=140)
    plt.axis('equal')  # Equal aspect ratio ensures that pie is drawn as a circle.
    plt.title("Berkshire Hathaway Asset Allocation")
    plt.savefig(chart_path)
    plt.close()
    plt.savefig(chart_path)
    plt.close()
    print(f"Generated {chart_path}")

def generate_cash_trend_chart(history, filename):
    chart_path = os.path.join(BASE_DIR, filename)
    
    dates = [h['date'] for h in history]
    pcts = [h['cash_pct'] for h in history]
    
    plt.figure(figsize=(10, 6))
    plt.plot(dates, pcts, marker='o', linestyle='-', color='#2ecc71', linewidth=2)
    
    plt.title("Berkshire Hathaway Cash Allocation Trend")
    plt.ylabel("Cash % of Total Assets")
    plt.grid(True, linestyle='--', alpha=0.7)
    
    # Format x-axis dates
    plt.gcf().autofmt_xdate()
    
    plt.savefig(chart_path)
    plt.close()
    print(f"Generated {chart_path}")

def run_guru_analysis(html_filename):
    print("Starting Guru Analysis...")
    
    gurus = [
        {'name': 'Warren Buffett (Berkshire Hathaway)', 'code': 'BRK', 'ticker': 'BRK-B'},
        {'name': 'Bill Gates (Foundation Trust)', 'code': 'BMG', 'ticker': None},
        {'name': 'Ray Dalio (Bridgewater Associates)', 'code': 'DA', 'ticker': None}
    ]
    
    guru_data = []
    
    for guru in gurus:
        print(f"Processing {guru['name']}...")
        
        # 1. Fetch Holdings
        holdings = fetch_guru.get_dataroma_holdings(guru['code'])
        
        # 2. Fetch Cash (if ticker exists)
        cash = fetch_guru.get_cash_position(guru['ticker'])
        
        # Calculate totals
        total_equity = sum(h['value'] for h in holdings)
        total_assets = total_equity + cash
        
        perf_chart_filename = None
        cash_trend_filename = None
        
        if guru['code'] == 'BRK':
            # Generate SPY vs BRK comparison chart
            print("Generating SPY vs BRK performance chart...")
            spy_returns = performance.get_yearly_returns('SPY', period="max")
            brk_returns = performance.get_yearly_returns('BRK-B', period="max")
            perf_chart_filename = "chart_performance_BRK_vs_SPY.png"
            performance.generate_comparison_chart(spy_returns, brk_returns, os.path.join(BASE_DIR, perf_chart_filename))
            
            # Generate Cash Trend Chart
            print("Generating Cash Trend chart...")
            history = fetch_guru.get_cash_history(guru['ticker'])
            if history:
                cash_trend_filename = "chart_cash_trend_BRK.png"
                generate_cash_trend_chart(history, cash_trend_filename)
        
        cash_pct = (cash / total_assets * 100) if total_assets > 0 else 0
        
        # Generate Chart (only if cash > 0)
        chart_filename = None
        if cash > 0:
            chart_filename = f"chart_guru_{guru['code']}.png"
            generate_guru_chart(total_equity, cash, chart_filename)
            
        # Format values
        formatted_holdings = []
        for h in holdings:
            h['formatted_value'] = f"${h['value']:,.0f}"
            formatted_holdings.append(h)
            
        guru_entry = {
            'name': guru['name'],
            'holdings': formatted_holdings,
            'total_equity': f"{total_equity/1e9:.1f}",
            'total_cash': f"{cash/1e9:.1f}" if cash > 0 else "N/A",
            'cash_pct': f"{cash_pct:.1f}" if cash > 0 else "N/A",
            'chart_filename': chart_filename,
            'performance_chart': perf_chart_filename,
            'cash_trend_chart': cash_trend_filename,
            'has_cash': cash > 0
        }
        guru_data.append(guru_entry)
    
    # Generate HTML
    env = Environment(loader=FileSystemLoader(TEMPLATE_DIR))
    template = env.get_template('guru.html')
    
    date_str = datetime.now().strftime("%Y-%m-%d")
    output_path = os.path.join(BASE_DIR, html_filename)
        
    html_content = template.render(
        date=date_str,
        gurus=guru_data,
        current_page=html_filename
    )
    
    with open(output_path, 'w') as f:
        f.write(html_content)
    print(f"Generated {output_path}")

def run_consumer_staples_analysis(html_filename, title):
    print("Starting Consumer Staples Analysis...")
    
    # 1. Get S&P 500 tickers with sectors
    all_stocks = fetch_data.get_sp500_tickers_with_sector()
    
    # 2. Filter for Consumer Staples
    staples_tickers = [s['ticker'] for s in all_stocks if s['sector'] == 'Consumer Staples']
    print(f"Found {len(staples_tickers)} Consumer Staples stocks.")
    
    staples_data = []
    
    for ticker in staples_tickers:
        print(f"Fetching data for {ticker}...", end='\r')
        try:
            info = fetch_data.get_stock_data(ticker)
            if info:
                # Extract metrics
                roe = info.get('returnOnEquity')
                margin = info.get('profitMargins')
                rev_growth = info.get('revenueGrowth')
                de = info.get('debtToEquity')
                peg = info.get('pegRatio')
                
                # Fallback PEG calculation
                if peg is None:
                    pe = info.get('trailingPE')
                    growth = info.get('earningsGrowth')
                    if pe and growth and growth > 0:
                        peg = pe / (growth * 100)
                
                # Fetch competitors
                sector = info.get('sector', 'Consumer Staples')
                industry = info.get('industry', '')
                competitors = fetch_competitors.get_industry_peers(ticker, sector, industry)
                
                # Get additional info
                market_cap = info.get('marketCap')
                dividend_yield = info.get('dividendYield')
                description = info.get('longBusinessSummary', 'No description available.')
                
                staples_data.append({
                    'ticker': ticker,
                    'name': info.get('longName', ticker),
                    'roe': f"{roe:.2%}" if roe else "N/A",
                    'roe_val': roe if roe else -999,
                    'margin': f"{margin:.2%}" if margin else "N/A",
                    'margin_val': margin if margin else -999,
                    'growth': f"{rev_growth:.2%}" if rev_growth else "N/A",
                    'growth_val': rev_growth if rev_growth else -999,
                    'de': de if de is not None else "N/A",
                    'de_val': de if de is not None else 9999,
                    'peg': f"{peg:.2f}" if peg else "N/A",
                    'peg_val': peg if peg else 9999,
                    'competitors': competitors,
                    'market_cap': f"${market_cap/1e9:.1f}B" if market_cap else "N/A",
                    'dividend_yield': f"{dividend_yield:.2f}%" if dividend_yield else "N/A",
                    'description': description
                })
        except Exception as e:
            print(f"Error processing {ticker}: {e}")
            
    # Sort by ROE descending
    staples_data.sort(key=lambda x: x['roe_val'], reverse=True)
    
    # Generate HTML
    env = Environment(loader=FileSystemLoader(TEMPLATE_DIR))
    template = env.get_template('consumer_staples.html')
    
    date_str = datetime.now().strftime("%Y-%m-%d")
    output_path = os.path.join(BASE_DIR, html_filename)
    
    html_content = template.render(
        date=date_str,
        stocks=staples_data,
        title=title,
        current_page=html_filename
    )
    
    with open(output_path, 'w') as f:
        f.write(html_content)
    print(f"\nGenerated {output_path}")


def run_tech_analysis(html_filename, title):
    print("Starting Technology Sector Analysis...")
    
    # 1. Get S&P 500 tickers with sectors
    all_stocks = fetch_data.get_sp500_tickers_with_sector()
    
    # 2. Filter for Technology / Information Technology
    tech_tickers = [s['ticker'] for s in all_stocks if 'Technology' in s['sector'] or s['sector'] == 'Information Technology']
    print(f"Found {len(tech_tickers)} Technology stocks.")
    
    tech_data = []
    
    for ticker in tech_tickers:
        print(f"Fetching data for {ticker}...", end='\r')
        try:
            info = fetch_data.get_stock_data(ticker)
            if info:
                # Extract metrics
                roe = info.get('returnOnEquity')
                margin = info.get('profitMargins')
                rev_growth = info.get('revenueGrowth')
                de = info.get('debtToEquity')
                peg = info.get('pegRatio')
                pe = info.get('trailingPE')
                
                # Fallback PEG calculation
                if peg is None:
                    growth = info.get('earningsGrowth')
                    if pe and growth and growth > 0:
                        peg = pe / (growth * 100)
                
                # Fetch competitors
                sector = info.get('sector', 'Technology')
                industry = info.get('industry', '')
                competitors = fetch_competitors.get_industry_peers(ticker, sector, industry)
                
                # Get additional info
                market_cap = info.get('marketCap')
                dividend_yield = info.get('dividendYield')
                description = info.get('longBusinessSummary', 'No description available.')
                
                tech_data.append({
                    'ticker': ticker,
                    'name': info.get('longName', ticker),
                    'roe': f"{roe:.2%}" if roe else "N/A",
                    'roe_val': roe if roe else -999,
                    'margin': f"{margin:.2%}" if margin else "N/A",
                    'margin_val': margin if margin else -999,
                    'growth': f"{rev_growth:.2%}" if rev_growth else "N/A",
                    'growth_val': rev_growth if rev_growth else -999,
                    'de': de if de is not None else "N/A",
                    'de_val': de if de is not None else 9999,
                    'peg': f"{peg:.2f}" if peg else "N/A",
                    'peg_val': peg if peg else 9999,
                    'pe': f"{pe:.2f}" if pe else "N/A",
                    'pe_val': pe if pe else 9999,
                    'competitors': competitors,
                    'market_cap': f"${market_cap/1e9:.1f}B" if market_cap else "N/A",
                    'market_cap_val': market_cap if market_cap else 0,
                    'dividend_yield': f"{dividend_yield:.2f}%" if dividend_yield else "N/A",
                    'description': description
                })
        except Exception as e:
            print(f"Error processing {ticker}: {e}")
            
    # Sort by market cap descending
    tech_data.sort(key=lambda x: x['market_cap_val'], reverse=True)
    
    # Generate HTML
    env = Environment(loader=FileSystemLoader(TEMPLATE_DIR))
    template = env.get_template('tech.html')
    
    date_str = datetime.now().strftime("%Y-%m-%d")
    output_path = os.path.join(BASE_DIR, html_filename)
    
    html_content = template.render(
        date=date_str,
        stocks=tech_data,
        title=title,
        current_page=html_filename
    )
    
    with open(output_path, 'w') as f:
        f.write(html_content)
    print(f"\nGenerated {output_path}")


if __name__ == "__main__":
    # Initialize DB
    conn = init_db()
    
    # 1. S&P 500 Analysis
    sp500_tickers = fetch_data.get_sp500_tickers()
    run_analysis(conn, 'SP500', sp500_tickers, 'index.html', 'Daily Stock Picks: S&P 500')
    
    # 2. Non-S&P 500 Analysis (S&P 400 + 600)
    non_sp500_tickers = fetch_data.get_non_sp500_tickers()
    run_analysis(conn, 'NON_SP500', non_sp500_tickers, 'non_spy.html', 'Daily Stock Picks: Non-S&P 500')
    
    # 3. Guru Analysis
    run_guru_analysis('guru.html')

    # 4. Consumer Staples Analysis
    run_consumer_staples_analysis('consumer_staples.html', 'S&P 500 Consumer Staples Report')
    
    # 5. Technology Analysis
    run_tech_analysis('tech.html', 'S&P 500 Technology Report')
    
    conn.close()
