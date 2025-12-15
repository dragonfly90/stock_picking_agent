import yfinance as yf

def get_china_tickers():
    """
    Returns a curated list of top Chinese A-share stocks (Blue Chips).
    Mix of Shanghai (.SS) and Shenzhen (.SZ) listings.
    """
    # Top stocks by market cap and popularity (Moutai, Banks, Tech, EV, etc.)
    tickers = [
        "600519.SS", # Kweichow Moutai (Consumer)
        "300750.SZ", # CATL (Batteries)
        "601318.SS", # Ping An Insurance (Finance)
        "600036.SS", # China Merchants Bank (Finance)
        "002594.SZ", # BYD (EV/Auto)
        "600276.SS", # Hengrui Medicine (Pharma)
        "000858.SZ", # Wuliangye (Consumer)
        "600900.SS", # Yangtze Power (Utilities)
        "000333.SZ", # Midea Group (Appliances)
        "601888.SS", # China Tourism Group Duty Free (Consumer)
        "603288.SS", # Foshan Haitian Flavouring (Consumer)
        "300015.SZ", # Aier Eye Hospital (Healthcare)
        "000651.SZ", # Gree Electric (Appliances)
        "601012.SS", # LONGi Green Energy (Solar)
        "600030.SS", # CITIC Securities (Finance)
        "002415.SZ", # Hikvision (Tech)
        "600887.SS", # Yili Group (Consumer)
        "600309.SS", # Wanhua Chemical (Materials)
        "002475.SZ", # Luxshare Precision (Tech/Apple Supplier)
        "601166.SS", # Industrial Bank (Finance)
        "600000.SS", # SPDB (Finance)
        "000001.SZ", # Ping An Bank (Finance)
        "601398.SS", # ICBC (Finance)
        "601288.SS", # Agricultural Bank of China (Finance)
        "601939.SS", # CCB (Finance)
        "601988.SS", # Bank of China (Finance)
        "601857.SS", # PetroChina (Energy)
        "600028.SS", # Sinopec (Energy)
        "601088.SS", # China Shenhua Energy (Energy)
        "300760.SZ", # Mindray Bio-Medical (Healthcare)
    ]
    return tickers

def get_stock_data(ticker):
    """
    Fetches data for a single stock using yfinance.
    """
    try:
        stock = yf.Ticker(ticker)
        info = stock.info
        return info
    except Exception as e:
        print(f"Error fetching data for {ticker}: {e}")
        return None

if __name__ == "__main__":
    # Test
    tickers = get_china_tickers()
    print(f"Found {len(tickers)} tickers.")
    print("Fetching data for first ticker...")
    data = get_stock_data(tickers[0])
    if data:
        print(f"Name: {data.get('longName')}")
        print(f"Market Cap: {data.get('marketCap')}")
