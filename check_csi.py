import akshare as ak
import pandas as pd

def check_csi():
    print("Fetching CSI 300 constituents...")
    try:
        # CSI 300
        df_300 = ak.index_stock_cons(symbol="000300")
        print(f"CSI 300: Found {len(df_300)} stocks.")
        print(df_300.head())
        
        # CSI 500
        print("\nFetching CSI 500 constituents...")
        df_500 = ak.index_stock_cons(symbol="000905")
        print(f"CSI 500: Found {len(df_500)} stocks.")
        print(df_500.head())
        
        return df_300, df_500
    except Exception as e:
        print(f"Error fetching CSI data: {e}")
        return None, None

if __name__ == "__main__":
    check_csi()
