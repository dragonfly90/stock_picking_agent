import yfinance as yf

# Test dividend yield for Clor ox
ticker = yf.Ticker("CLX")
info = ticker.info

print(f"Ticker: CLX")
print(f"dividendYield: {info.get('dividendYield')}")
print(f"dividendRate: {info.get('dividendRate')}")
print(f"Formatted: {info.get('dividendYield'):.2%}" if info.get('dividendYield') else "N/A")

# Try another
ticker2 = yf.Ticker("PG")
info2 = ticker2.info
print(f"\nTicker: PG")
print(f"dividendYield: {info2.get('dividendYield')}")
print(f"dividendRate: {info2.get('dividendRate')}")
print(f"Formatted: {info2.get('dividendYield'):.2%}" if info2.get('dividendYield') else "N/A")
