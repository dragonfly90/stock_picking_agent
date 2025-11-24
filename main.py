import fetch_data
import analyze
import time

def main():
    print("Starting Stock Selection Agent...")
    
    # 1. Get Tickers
    print("Fetching S&P 500 tickers...")
    tickers = fetch_data.get_sp500_tickers()
    if not tickers:
        print("Failed to fetch tickers. Exiting.")
        return

    print(f"Found {len(tickers)} tickers. Analyzing top candidates...")
    
    # For demonstration/speed, we might limit to a subset if the user wants a quick result,
    # but the request is for the "top stock", so we should ideally check them all.
    # However, checking 500 stocks with yfinance sequentially is slow and might hit rate limits.
    # Let's try a batch of 20 first to prove it works, then we can discuss full run.
    # OR better: just run for all but handle errors gracefully.
    # To avoid rate limits, we can add a small sleep.
    
    # Let's limit to 50 for this initial run to be responsive.
    # tickers = tickers[:50] 
    
    stocks_data = []
    # Process in chunks or just loop with progress
    count = 0
    total = len(tickers)
    
    # Optimization: yfinance can fetch multiple tickers at once? 
    # yf.Tickers(' '.join(tickers)) might be faster but 'info' attribute fetching is still often per-ticker.
    # Let's stick to loop for simplicity and reliability.
    
    for ticker in tickers:
        count += 1
        print(f"[{count}/{total}] Fetching data for {ticker}...", end='\r')
        try:
            info = fetch_data.get_stock_data(ticker)
            if info:
                stocks_data.append((ticker, info))
        except Exception as e:
            pass
        
        # Rate limit protection
        # time.sleep(0.1) 
        
        # BREAK EARLY FOR DEMO if needed (remove for full run)
        if count >= 20: 
             break

    print("\nAnalysis complete. Ranking stocks...")
    ranked_stocks = analyze.rank_stocks(stocks_data)

    if not ranked_stocks:
        print("No stocks met the criteria or data fetching failed.")
        return

    top_pick = ranked_stocks[0]
    print("\n" + "="*40)
    print(f"TOP RECOMMENDATION: {top_pick['ticker']}")
    print("="*40)
    print(f"Score: {top_pick['score']}/5")
    print("Details:")
    for detail in top_pick['details']:
        print(f" - {detail}")
    
    print("\nTop 5 Candidates:")
    for i, stock in enumerate(ranked_stocks[:5]):
        print(f"{i+1}. {stock['ticker']} (Score: {stock['score']}, PEG: {stock['metrics']['peg']})")
        print("Details:")
        for detail in stock['details']:
            print(f" - {detail}")
import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

def send_email(subject, body):
    sender_email = os.environ.get('EMAIL_USER')
    sender_password = os.environ.get('EMAIL_PASSWORD')
    receiver_email = os.environ.get('EMAIL_TO')

    if not sender_email or not sender_password or not receiver_email:
        print("Email credentials not found. Skipping email.")
        return

    msg = MIMEMultipart()
    msg['From'] = sender_email
    msg['To'] = receiver_email
    msg['Subject'] = subject
    msg.attach(MIMEText(body, 'plain'))

    try:
        # Connect to Gmail's SMTP server
        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as server:
            server.login(sender_email, sender_password)
            server.send_message(msg)
        print("Email sent successfully!")
    except Exception as e:
        print(f"Failed to send email: {e}")

if __name__ == "__main__":
    # Capture output for email
    import io
    import sys
    
    # Redirect stdout to capture the report
    old_stdout = sys.stdout
    new_stdout = io.StringIO()
    sys.stdout = new_stdout
    
    main()
    
    # Restore stdout
    output = new_stdout.getvalue()
    sys.stdout = old_stdout
    print(output) # Print to console as well
    
    # Send email if credentials exist
    if "TOP RECOMMENDATION" in output:
        send_email("Daily Stock Pick Report", output)
