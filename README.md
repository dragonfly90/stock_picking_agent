# Stock Selection Agent

A Python-based agent that analyzes S&P 500 stocks to recommend top candidates for a long-term (> 5 years) buy and hold strategy.

## 🌐 Web Dashboard
**View the Daily Report:** [https://dragonfly90.github.io/stock_picking_agent/](https://dragonfly90.github.io/stock_picking_agent/)

*(Note: Ensure GitHub Pages is enabled in Settings -> Pages -> Source: Deploy from branch 'main')*

## Strategy: QGARP (Quality + Growth at a Reasonable Price)

The agent scores stocks from **0 to 5** based on the following fundamental criteria. A stock gets **+1 point** for each criterion it meets:

1.  **Return on Equity (ROE) > 15%**
    *   **What it is**: Measures how efficiently a company uses shareholder money to generate profit.
    *   **Why**: High ROE indicates a high-quality business with a competitive advantage (moat).

2.  **Profit Margin > 10%**
    *   **What it is**: The percentage of revenue that turns into net profit.
    *   **Why**: Ensures the company has pricing power and isn't in a low-margin commodity business.

3.  **Revenue Growth > 5%**
    *   **What it is**: The year-over-year increase in sales.
    *   **Why**: We want companies that are expanding, not stagnant.

4.  **Debt-to-Equity Ratio < 0.5 (< 50%)**
    *   **What it is**: A measure of financial leverage.
    *   **Why**: Low debt companies are safer and less likely to face bankruptcy during economic downturns.

5.  **PEG Ratio < 2.0**
    *   **What it is**: Price/Earnings ratio divided by Annual Earnings Growth Rate.
    *   **Why**: Determines if a stock is undervalued relative to its growth. A PEG < 1.0 is considered cheap; < 2.0 is reasonable.

## Sample Results (Nov 2025)

After analyzing a subset of the S&P 500, the agent identified **Alphabet Inc. (GOOGL)** as the top recommendation.

### Top Pick: GOOGL (Score: 5/5)
| Metric | Value | Criteria | Result |
| :--- | :--- | :--- | :--- |
| **ROE** | 35.45% | > 15% | ✅ Pass |
| **Profit Margin** | 32.23% | > 10% | ✅ Pass |
| **Revenue Growth** | 15.90% | > 5% | ✅ Pass |
| **Debt/Equity** | 11.42% | < 50% | ✅ Pass |
| **PEG Ratio** | 0.84 | < 2.0 | ✅ Pass |

### Top 5 Candidates
1. **GOOGL** (Score: 5, PEG: 0.84)
2. **Allstate Corp (ALL)** (Score: 4, PEG: 0.03)
3. **A. O. Smith (AOS)** (Score: 4, PEG: 1.20)
4. **Agilent Technologies (A)** (Score: 4, PEG: 1.64)
5. **Advanced Micro Devices (AMD)** (Score: 4, PEG: 1.76)

## Usage

1. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

2. **Run the Agent**
   ```bash
   python3 main.py
   ```
