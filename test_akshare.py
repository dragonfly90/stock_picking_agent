import akshare as ak
import time

def test_full_market_data():
    print("Fetching all A-share spot data...")
    start_time = time.time()
    try:
        # stock_zh_a_spot_em: East Money real-time data for all A-shares
        df = ak.stock_zh_a_spot_em()
        end_time = time.time()
        
        print(f"Fetched {len(df)} stocks in {end_time - start_time:.2f} seconds.")
        print("Columns:", df.columns.tolist())
        print("\nFirst 5 rows:")
        print(df.head())
        
        # Check if we have key metrics
        required_cols = ['代码', '名称', '最新价', '涨跌幅', '市盈率-动态', '市净率', '总市值']
        missing = [col for col in required_cols if col not in df.columns]
        if missing:
            print(f"\nMissing columns: {missing}")
        else:
            print("\nAll key columns found.")
            
    except Exception as e:
        print(f"Error fetching data: {e}")

if __name__ == "__main__":
    test_full_market_data()
