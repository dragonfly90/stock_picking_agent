def score_stock(info):
    """
    Scores a stock based on QGARP criteria.
    Returns a dictionary with score and details.
    """
    score = 0
    details = []

    if not info:
        return {'score': -1, 'details': ['No data']}

    # 1. ROE > 15%
    roe = info.get('returnOnEquity', 0)
    if roe and roe > 0.15:
        score += 1
        details.append(f"ROE: {roe:.2%} (>15%)")
    else:
        details.append(f"ROE: {roe:.2%} (<=15%)")

    # 2. Profit Margin > 10%
    margin = info.get('profitMargins', 0)
    if margin and margin > 0.10:
        score += 1
        details.append(f"Margin: {margin:.2%} (>10%)")
    else:
        details.append(f"Margin: {margin:.2%} (<=10%)")

    # 3. Revenue Growth (using revenueGrowth or earningsGrowth as proxy if historical not avail)
    # yfinance 'revenueGrowth' is usually quarterly yoy.
    rev_growth = info.get('revenueGrowth', 0)
    if rev_growth and rev_growth > 0.05:
        score += 1
        details.append(f"Rev Growth: {rev_growth:.2%} (>5%)")
    else:
        details.append(f"Rev Growth: {rev_growth:.2%} (<=5%)")

    # 4. Debt/Equity < 0.5 (yfinance uses debtToEquity which is usually a percentage, e.g. 50 for 0.5)
    # Wait, yfinance debtToEquity is often returned as a percentage (e.g. 150.5 means 1.505)
    # Let's check the data format. Usually it's a number like 0.5 or 50.
    # Standard yfinance is percentage. So < 50 is < 0.5 ratio.
    de = info.get('debtToEquity', 1000)
    if de is not None and de < 50:
        score += 1
        details.append(f"D/E: {de} (<50%)")
    else:
        details.append(f"D/E: {de} (>=50%)")

    # 5. PEG Ratio < 2.0
    peg = info.get('pegRatio')

    # Fallback: Calculate PEG if missing
    if peg is None:
        pe = info.get('trailingPE')
        growth = info.get('earningsGrowth') # This is usually a decimal, e.g. 0.35 for 35%
        if pe and growth and growth > 0:
            peg = pe / (growth * 100)

    if peg is not None and peg < 2.0 and peg > 0:
        score += 1
        details.append(f"PEG: {peg:.2f} (<2.0)")
    else:
        val = f"{peg:.2f}" if peg is not None else "N/A"
        details.append(f"PEG: {val} (>=2.0 or invalid)")

    # 6. Free Cash Flow Yield > 3%
    fcf = info.get('freeCashflow')
    market_cap = info.get('marketCap')
    if fcf and market_cap and market_cap > 0 and (fcf / market_cap) > 0.03:
        score += 1
        details.append(f"FCF Yield: {fcf/market_cap:.2%} (>3%)")
    else:
        fcf_yield = (fcf / market_cap) if (fcf and market_cap and market_cap > 0) else None
        val = f"{fcf_yield:.2%}" if fcf_yield is not None else "N/A"
        details.append(f"FCF Yield: {val} (<=3% or N/A)")

    # 7. 52-week position < 70%
    last_price = info.get('currentPrice')
    high52 = info.get('fiftyTwoWeekHigh')
    low52 = info.get('fiftyTwoWeekLow')
    w52_position = None
    if last_price and high52 and low52 and (high52 - low52) > 0:
        w52_position = (last_price - low52) / (high52 - low52)
    if w52_position is not None and w52_position < 0.70:
        score += 1
        details.append(f"52W Position: {w52_position:.2%} (<70%)")
    else:
        val = f"{w52_position:.2%}" if w52_position is not None else "N/A"
        details.append(f"52W Position: {val} (>=70% or N/A)")

    return {
        'score': score,
        'details': details,
        'metrics': {
            'roe': roe,
            'margin': margin,
            'rev_growth': rev_growth,
            'de': de,
            'peg': peg,
            'pe': info.get('trailingPE'),
            'dividend_yield': info.get('dividendYield'),
            'industry': info.get('industry'),
            'sector': info.get('sector'),
            'w52_position': w52_position
        }
    }

def rank_stocks(stocks_data):
    """
    Ranks stocks by score (0-7), then by PEG ratio (ascending).
    stocks_data: list of (ticker, info) tuples
    """
    scored_stocks = []
    for ticker, info in stocks_data:
        result = score_stock(info)
        if result['score'] >= 0: # Filter out failed fetches
            scored_stocks.append({
                'ticker': ticker,
                'score': result['score'],
                'details': result['details'],
                'metrics': result['metrics']
            })
    
    # Sort by Score (desc), then PEG (asc)
    # We handle None PEG by treating it as infinity for sorting
    scored_stocks.sort(key=lambda x: (
        -x['score'], 
        x['metrics']['peg'] if x['metrics']['peg'] is not None else float('inf')
    ))
    
    return scored_stocks
