"""
fetch_energy_data.py
Fetches oil/energy commodity prices, energy ETFs, and energy stock data.
"""

import yfinance as yf
import pandas as pd

# ── Commodity futures traded on yfinance ────────────────────────────────────
COMMODITIES = {
    'WTI Crude Oil':   'CL=F',
    'Brent Crude Oil': 'BZ=F',
    'Natural Gas':     'NG=F',
    'RBOB Gasoline':   'RB=F',
    'Heating Oil':     'HO=F',
}

# ── Energy ETFs ──────────────────────────────────────────────────────────────
ENERGY_ETFS = {
    # Broad energy sector
    'XLE':  'Energy Select Sector SPDR Fund',
    'VDE':  'Vanguard Energy ETF',
    'IYE':  'iShares U.S. Energy ETF',
    'FENY': 'Fidelity MSCI Energy Index ETF',
    # Oil-specific
    'USO':  'United States Oil Fund',
    'BNO':  'United States Brent Oil Fund',
    'DBO':  'Invesco DB Oil Fund',
    # Natural gas
    'UNG':  'United States Natural Gas Fund',
    'BOIL': 'ProShares Ultra Bloomberg Natural Gas',
    # Oil services
    'OIH':  'VanEck Oil Services ETF',
    'XES':  'SPDR S&P Oil & Gas Equipment & Services ETF',
    # E&P
    'XOP':  'SPDR S&P Oil & Gas Explor & Prod ETF',
}

# ── Key energy stocks ────────────────────────────────────────────────────────
ENERGY_STOCKS = {
    # Integrated majors
    'XOM':  'ExxonMobil',
    'CVX':  'Chevron',
    'COP':  'ConocoPhillips',
    'BP':   'BP plc',
    'SHEL': 'Shell plc',
    'TTE':  'TotalEnergies',
    'E':    'Eni SpA',
    # Oil services & equipment
    'SLB':  'SLB (Schlumberger)',
    'HAL':  'Halliburton',
    'BKR':  'Baker Hughes',
    # Refiners & marketing
    'MPC':  'Marathon Petroleum',
    'VLO':  'Valero Energy',
    'PSX':  'Phillips 66',
    'PBF':  'PBF Energy',
    # Pipelines & MLPs
    'KMI':  'Kinder Morgan',
    'WMB':  'Williams Companies',
    'ET':   'Energy Transfer LP',
    'EPD':  'Enterprise Products Partners',
    'MMP':  'Magellan Midstream Partners',
    # E&P
    'EOG':  'EOG Resources',
    'DVN':  'Devon Energy',
    'FANG': 'Diamondback Energy',
    'APA':  'APA Corporation',
    'OXY':  'Occidental Petroleum',
    'MRO':  'Marathon Oil',
    'AR':   'Antero Resources',
    'RRC':  'Range Resources',
    # Coal & other
    'BTU':  'Peabody Energy',
    'ARCH': 'Arch Resources',
}


def get_commodity_prices():
    """
    Returns a list of dicts with current commodity price snapshot.
    """
    results = []
    for name, ticker in COMMODITIES.items():
        try:
            t = yf.Ticker(ticker)
            hist = t.history(period='5d')
            if hist.empty:
                results.append({'name': name, 'ticker': ticker, 'price': None,
                                 'change': None, 'change_pct': None})
                continue

            latest = hist['Close'].iloc[-1]
            prev   = hist['Close'].iloc[-2] if len(hist) > 1 else latest
            change = latest - prev
            change_pct = (change / prev * 100) if prev else 0

            results.append({
                'name':       name,
                'ticker':     ticker,
                'price':      round(latest, 3),
                'change':     round(change, 3),
                'change_pct': round(change_pct, 2),
            })
        except Exception as e:
            print(f"Error fetching commodity {ticker}: {e}")
            results.append({'name': name, 'ticker': ticker, 'price': None,
                             'change': None, 'change_pct': None})
    return results


def get_commodity_history(ticker, period='1y'):
    """Returns a DataFrame of daily closes for a commodity ticker."""
    try:
        t = yf.Ticker(ticker)
        hist = t.history(period=period)
        return hist[['Close']] if not hist.empty else pd.DataFrame()
    except Exception as e:
        print(f"Error fetching commodity history {ticker}: {e}")
        return pd.DataFrame()


def get_etf_data():
    """
    Returns a list of dicts with ETF performance metrics.
    """
    results = []
    for ticker, name in ENERGY_ETFS.items():
        try:
            t = yf.Ticker(ticker)
            info = t.info
            hist = t.history(period='1y')

            price = info.get('regularMarketPrice') or info.get('previousClose')
            prev_close = info.get('previousClose')
            change     = (price - prev_close) if (price and prev_close) else None
            change_pct = (change / prev_close * 100) if (change and prev_close) else None

            # YTD return
            ytd_ret = None
            if not hist.empty:
                start_of_year = hist[hist.index.year == hist.index[-1].year].iloc[0]['Close']
                end_price     = hist.iloc[-1]['Close']
                ytd_ret       = round((end_price - start_of_year) / start_of_year * 100, 2)

            # 1-year return
            one_yr_ret = None
            if len(hist) >= 250:
                one_yr_ret = round(
                    (hist.iloc[-1]['Close'] - hist.iloc[0]['Close']) / hist.iloc[0]['Close'] * 100, 2)

            results.append({
                'ticker':     ticker,
                'name':       name,
                'price':      round(price, 2) if price else None,
                'change':     round(change, 2) if change else None,
                'change_pct': round(change_pct, 2) if change_pct else None,
                'ytd_ret':    ytd_ret,
                'one_yr_ret': one_yr_ret,
                'aum':        info.get('totalAssets'),
                'expense':    info.get('annualReportExpenseRatio'),
            })
        except Exception as e:
            print(f"Error fetching ETF {ticker}: {e}")
            results.append({'ticker': ticker, 'name': name, 'price': None,
                             'change': None, 'change_pct': None,
                             'ytd_ret': None, 'one_yr_ret': None,
                             'aum': None, 'expense': None})
    return results


def get_energy_stock_data(ticker):
    """
    Returns a dict of financial metrics for a single energy stock.
    Uses the same yfinance .info approach as the rest of the project.
    """
    try:
        t = yf.Ticker(ticker)
        info = t.info
        if not info:
            return None

        price     = info.get('regularMarketPrice') or info.get('previousClose')
        prev      = info.get('previousClose')
        change    = (price - prev) if (price and prev) else None
        change_pct = (change / prev * 100) if (change and prev) else None

        peg = info.get('pegRatio')
        pe  = info.get('trailingPE')
        if peg is None:
            growth = info.get('earningsGrowth')
            if pe and growth and growth > 0:
                peg = pe / (growth * 100)

        return {
            'ticker':        ticker,
            'name':          info.get('longName', ticker),
            'price':         round(price, 2) if price else None,
            'change':        round(change, 2) if change else None,
            'change_pct':    round(change_pct, 2) if change_pct else None,
            'market_cap':    info.get('marketCap'),
            'pe':            round(pe, 2) if pe else None,
            'peg':           round(peg, 2) if peg else None,
            'roe':           info.get('returnOnEquity'),
            'margin':        info.get('profitMargins'),
            'rev_growth':    info.get('revenueGrowth'),
            'de':            info.get('debtToEquity'),
            'dividend_yield':info.get('dividendYield'),
            'beta':          info.get('beta'),
            'description':   info.get('longBusinessSummary', ''),
            'industry':      info.get('industry', ''),
            'sector':        info.get('sector', ''),
            'sub_sector':    ENERGY_STOCKS.get(ticker, ''),
        }
    except Exception as e:
        print(f"Error fetching energy stock {ticker}: {e}")
        return None


def get_all_energy_stocks():
    """
    Fetches data for all energy stocks and returns a sorted list.
    Sorted by market cap descending.
    """
    results = []
    total = len(ENERGY_STOCKS)
    for i, ticker in enumerate(ENERGY_STOCKS, 1):
        print(f"[{i}/{total}] Fetching {ticker}...", end='\r')
        data = get_energy_stock_data(ticker)
        if data:
            results.append(data)

    # Sort by market cap, largest first; None values go last
    results.sort(key=lambda x: x['market_cap'] or 0, reverse=True)
    return results


def get_energy_stock_history(ticker, period='1y'):
    """Returns history DataFrame for an energy stock."""
    try:
        t = yf.Ticker(ticker)
        hist = t.history(period=period)
        return hist if not hist.empty else pd.DataFrame()
    except Exception as e:
        print(f"Error fetching history for {ticker}: {e}")
        return pd.DataFrame()
