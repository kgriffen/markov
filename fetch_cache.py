"""
Fetch 10 years of daily closes for each ticker and write to cache/.
Run locally or via GitHub Actions.
"""
import json
import sys
import warnings
from pathlib import Path

warnings.filterwarnings("ignore")

import yfinance as yf
import pandas as pd

TICKERS = ["SPY", "QQQ", "IWM", "USO", "UNG", "FXE", "FXI", "IBIT", "IYR", "GLD", "SLV"]

Path("cache").mkdir(exist_ok=True)

errors = []
for ticker in TICKERS:
    try:
        df = yf.download(ticker, period="10y", interval="1d", auto_adjust=True, progress=False)
        if isinstance(df.columns, pd.MultiIndex):
            df.columns = df.columns.get_level_values(0)
        close = df["Close"].dropna()
        payload = {
            "ticker":  ticker,
            "closes":  [round(float(v), 4) for v in close.tolist()],
            "updated": close.index[-1].strftime("%Y-%m-%d"),
            "rows":    len(close),
        }
        out = Path(f"cache/{ticker}.json")
        out.write_text(json.dumps(payload))
        print(f"  {ticker}: {payload['rows']} rows → {payload['updated']}")
    except Exception as exc:
        print(f"  {ticker}: ERROR — {exc}")
        errors.append(ticker)

if errors:
    print(f"\nFailed tickers: {errors}")
    sys.exit(1)

print("\nCache written to cache/")
