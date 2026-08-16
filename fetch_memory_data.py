"""
Fetch Korean memory leader data (SK Hynix, Samsung) via yfinance.
Used as a leading indicator for US memory/chip stocks.
"""
import yfinance as yf
from datetime import datetime, timedelta

KR_MEMORY = {
    '000660.KS': {'name': 'SK Hynix',            'role': 'HBM3E leader (NVIDIA sole supplier)'},
    '005930.KS': {'name': 'Samsung Electronics',  'role': 'DRAM + NAND + Foundry'},
}

def get_kr_memory_data():
    results = {}
    for ticker, meta in KR_MEMORY.items():
        try:
            t = yf.Ticker(ticker)
            info = t.info
            hist = t.history(period='5d')
            if hist.empty:
                results[ticker] = {**meta, 'error': 'No data'}
                continue
            last_close = float(hist['Close'].iloc[-1])
            prev_close = float(hist['Close'].iloc[-2]) if len(hist) >= 2 else last_close
            chg_pct = (last_close - prev_close) / prev_close * 100 if prev_close else 0
            results[ticker] = {
                **meta,
                'ticker': ticker,
                'price': last_close,
                'price_fmt': f"₩{last_close:,.0f}",
                'change_pct': round(chg_pct, 2),
                'market_cap': info.get('marketCap'),
                'pe': info.get('trailingPE'),
                'session_date': hist.index[-1].strftime('%Y-%m-%d'),
            }
        except Exception as e:
            results[ticker] = {**meta, 'ticker': ticker, 'error': str(e)}
    return results
