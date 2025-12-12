import fetch_guru

history = fetch_guru.get_cash_history("BRK-B")
print(f"Found {len(history)} history points.")
for h in history:
    print(f"Date: {h['date'].date()}, Cash %: {h['cash_pct']:.2f}%, Cash: ${h['cash_val']/1e9:.1f}B")
