import yfinance as yf

# Check a few stocks to see what their actual dividend yields are
stocks = ['CLX', 'PG', 'KO']

for ticker in stocks:
    stock = yf.Ticker(ticker)
    info = stock.info
    
    div_yield_raw = info.get('dividendYield')
    div_rate = info.get('dividendRate')
    current_price = info.get('currentPrice') or info.get('regularMarketPrice')
    
    print(f"\n{ticker}:")
    print(f"  dividendYield (raw): {div_yield_raw}")
    print(f"  dividendRate (annual $): {div_rate}")
    print(f"  currentPrice: {current_price}")
    
    if div_rate and current_price:
        calculated_yield = (div_rate / current_price) * 100
        print(f"  Calculated Yield: {calculated_yield:.2f}%")
