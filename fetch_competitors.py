import requests
from bs4 import BeautifulSoup
import yfinance as yf

def get_competitors_via_search(ticker, industry, max_results=5):
    """
    Use web search to identify competitors for a given stock.
    Returns a list of competitor ticker symbols.
    """
    try:
        # Search query
        query = f"{ticker} competitors {industry} stock tickers"
        search_url = f"https://www.google.com/search?q={query.replace(' ', '+')}"
        
        headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        }
        
        # Note: This is a simplified approach. In production, you'd want to use
        # a more reliable method (e.g., scraping from financial sites or using an API)
        # For this demo, I'll return a hardcoded list based on common industries
        
        # Fallback: Use industry-based common competitors
        # This is a simplified demo - in practice you'd want a more robust solution
        competitors = []
        
        print(f"Identifying competitors for {ticker} in {industry}...")
        # Return empty for now - web scraping Google is unreliable and against TOS
        # A better approach would be to use a financial API or manually curated list
        
        return competitors[:max_results]
        
    except Exception as e:
        print(f"Error finding competitors for {ticker}: {e}")
        return []

def compare_stocks(tickers):
    """
    Fetch and compare key metrics for a list of tickers.
    Returns a list of dictionaries with ticker and metrics.
    """
    comparison = []
    
    for ticker in tickers:
        try:
            stock = yf.Ticker(ticker)
            info = stock.info
            
            comparison.append({
                'ticker': ticker,
                'name': info.get('shortName', ticker),
                'market_cap': info.get('marketCap'),
                'pe': info.get('trailingPE'),
                'peg': info.get('pegRatio'),
                'dividend_yield': info.get('dividendYield'),
                'revenue_growth': info.get('revenueGrowth')
            })
        except Exception as e:
            print(f"Error fetching data for {ticker}: {e}")
            continue
    
    return comparison

def get_industry_peers(ticker, sector, industry, max_peers=4):
    """
    Get industry peers for a stock.
    This is a demo implementation - returns a curated list based on sector.
    In production, you'd use a financial data API.
    """
    # Curated peer lists for common sectors (demo only)
    sector_peers = {
        'Technology': {
            'AAPL': ['MSFT', 'GOOGL', 'META', 'NVDA'],
            'MSFT': ['AAPL', 'GOOGL', 'AMZN', 'ORCL'],
            'GOOGL': ['META', 'AAPL', 'MSFT', 'AMZN'],
            'NVDA': ['AMD', 'INTC', 'QCOM', 'AVGO'],
            'AMD': ['NVDA', 'INTC', 'QCOM', 'MU'],
            'AVGO': ['NVDA', 'QCOM', 'TXN', 'ADI'],
            'INTC': ['AMD', 'NVDA', 'TSM', 'QCOM'],
            'QCOM': ['NVDA', 'AMD', 'AVGO', 'MRVL'],
            'TXN': ['ADI', 'NXPI', 'ON', 'MCHP'],
            'MU': ['NVDA', 'AMD', 'INTC', 'TSM'],
            'AMAT': ['LRCX', 'KLAC', 'ASML', 'TSM'],
            'LRCX': ['AMAT', 'KLAC', 'ASML', 'TSM'],
            'SNPS': ['CDNS', 'ARM', 'MRVL', 'AVGO'],
            'CDNS': ['SNPS', 'ARM', 'MRVL', 'AVGO'],
            'CRM': ['NOW', 'PLTR', 'ORCL', 'SAP'],
            'PLTR': ['CRM', 'AI', 'NOW', 'SNOW'],
            'NOW': ['CRM', 'PLTR', 'DDOG', 'SNOW'],
            'CRWD': ['PANW', 'DDOG', 'NOW', 'PLTR'],
            'PANW': ['CRWD', 'DDOG', 'NOW', 'PLTR'],
        },
        'Consumer Cyclical': {
            'AMZN': ['WMT', 'TGT', 'HD', 'LOW'],
            'TSLA': ['GM', 'F', 'NIO', 'RIVN'],
        },
        'Healthcare': {
            'JNJ': ['PFE', 'UNH', 'ABBV', 'MRK'],
            'UNH': ['CVS', 'CI', 'HUM', 'ELV'],
            'ISRG': ['ABT', 'MDT', 'SYK', 'BSX'],
        },
        'Financial Services': {
            'JPM': ['BAC', 'WFC', 'C', 'GS'],
            'BAC': ['JPM', 'WFC', 'C', 'USB'],
            'V': ['MA', 'AXP', 'PYPL', 'SQ'],
        },
        'Communication Services': {
            'META': ['GOOGL', 'SNAP', 'PINS', 'TWTR'],
        },
        'Consumer Defensive': {
            'KO': ['PEP', 'MNST', 'DPS', 'KDP'],
            'PG': ['UL', 'CL', 'KMB', 'CLX'],
        },
        'Energy': {
            'XOM': ['CVX', 'COP', 'SLB', 'EOG'],
        },
        'Industrials': {
            'BA': ['LMT', 'RTX', 'GE', 'HON'],
            'CAT': ['DE', 'CMI', 'EMR', 'ITW'],
        }
    }
    
    # Try to find ticker in our curated list
    if sector in sector_peers and ticker in sector_peers[sector]:
        return sector_peers[sector][ticker][:max_peers]
    
    # Fallback: return empty list
    print(f"No curated peers found for {ticker} in {sector}")
    return []

if __name__ == "__main__":
    # Test
    peers = get_industry_peers('AAPL', 'Technology', 'Consumer Electronics')
    print(f"Peers for AAPL: {peers}")
    
    if peers:
        comparison = compare_stocks(['AAPL'] + peers)
        for stock in comparison:
            print(stock)
