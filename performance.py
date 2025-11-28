import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import fetch_data

def get_yearly_returns(ticker, period="max"):
    """
    Fetch stock history and calculate yearly returns.
    Returns a Series of yearly % changes.
    """
    hist = fetch_data.get_stock_history(ticker, period=period)
    if hist is None or hist.empty:
        return None
    
    # Resample to yearly and take the last price of each year
    yearly_prices = hist['Close'].resample('Y').last()
    
    # Calculate percentage change
    yearly_returns = yearly_prices.pct_change() * 100
    
    # Drop the first NaN value
    yearly_returns = yearly_returns.dropna()
    
    # Convert index to just year integers
    yearly_returns.index = yearly_returns.index.year
    
    return yearly_returns

def calculate_averages(yearly_returns):
    """
    Calculate 5, 10, and 20 year average returns.
    Returns a dictionary.
    """
    if yearly_returns is None or yearly_returns.empty:
        return {}
        
    averages = {}
    
    # Get the last N years
    years = [5, 10, 20]
    
    for year in years:
        if len(yearly_returns) >= year:
            # Calculate simple average (arithmetic mean)
            # Alternatively, could use CAGR, but simple average is often requested for "average yearly return"
            avg = yearly_returns.tail(year).mean()
            averages[f'{year}y'] = avg
        else:
            averages[f'{year}y'] = None
            
    return averages

def generate_comparison_chart(spy_returns, brk_returns, filename):
    """
    Generate a grouped bar chart comparing SPY and BRK returns.
    """
    if spy_returns is None or brk_returns is None:
        print("Missing return data for chart.")
        return

    # Align data (intersection of years)
    common_years = spy_returns.index.intersection(brk_returns.index)
    
    # Filter to last 20 years max for readability, or use all common if less
    if len(common_years) > 20:
        common_years = common_years[-20:]
        
    spy_data = spy_returns.loc[common_years]
    brk_data = brk_returns.loc[common_years]
    
    # Setup plot
    fig, ax = plt.subplots(figsize=(14, 7))
    
    x = np.arange(len(common_years))
    width = 0.35
    
    rects1 = ax.bar(x - width/2, spy_data, width, label='S&P 500 (SPY)', color='#3498db')
    rects2 = ax.bar(x + width/2, brk_data, width, label='Berkshire (BRK-B)', color='#2ecc71')
    
    # Add labels
    ax.set_ylabel('Yearly Return (%)')
    ax.set_title('Yearly Performance: S&P 500 vs. Berkshire Hathaway (Last 20 Years)')
    ax.set_xticks(x)
    ax.set_xticklabels(common_years)
    ax.legend()
    
    # Add grid
    ax.grid(axis='y', linestyle='--', alpha=0.7)
    
    # Calculate averages for annotation
    spy_avgs = calculate_averages(spy_returns)
    brk_avgs = calculate_averages(brk_returns)
    
    # Create annotation text
    stats_text = "Average Yearly Returns:\n\n"
    stats_text += f"{'Period':<10} {'SPY':<10} {'BRK-B':<10}\n"
    stats_text += "-" * 30 + "\n"
    
    for period in ['5y', '10y', '20y']:
        s_val = f"{spy_avgs.get(period, 0):.1f}%" if spy_avgs.get(period) is not None else "N/A"
        b_val = f"{brk_avgs.get(period, 0):.1f}%" if brk_avgs.get(period) is not None else "N/A"
        stats_text += f"{period:<10} {s_val:<10} {b_val:<10}\n"
        
    # Add text box
    props = dict(boxstyle='round', facecolor='white', alpha=0.9)
    ax.text(0.02, 0.95, stats_text, transform=ax.transAxes, fontsize=10,
            verticalalignment='top', bbox=props, family='monospace')
            
    plt.tight_layout()
    plt.savefig(filename)
    plt.close()
    print(f"Generated {filename}")

if __name__ == "__main__":
    # Test
    print("Fetching returns...")
    spy = get_yearly_returns("SPY")
    brk = get_yearly_returns("BRK-B")
    
    if spy is not None and brk is not None:
        print("SPY Returns (last 5):", spy.tail(5))
        print("BRK Returns (last 5):", brk.tail(5))
        generate_comparison_chart(spy, brk, "test_comparison.png")
