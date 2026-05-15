import yfinance as yf
import pandas as pd
from datetime import date, datetime
from pathlib import Path

# --------------------------------------------------
# Configuration
# --------------------------------------------------
TICKER = "AVGO"
MIN_VOLUME = 3000
DATA_PATH = Path("C:/Users/B Dog/Documents/options_scanner/avgo_options.csv")
TODAY = date.today().isoformat()

# --------------------------------------------------
# Helpers
# --------------------------------------------------
def get_nearest_expiration(ticker: yf.Ticker) -> str:
    """Return the nearest non-expired option expiration."""
    today = date.today()
    expirations = ticker.options

    future_exps = [
        exp for exp in expirations
        if datetime.strptime(exp, "%Y-%m-%d").date() >= today
    ]

    return min(
        future_exps,
        key=lambda x: datetime.strptime(x, "%Y-%m-%d").date()
    )


def filter_options(df: pd.DataFrame, option_type: str) -> pd.DataFrame:
    """Filter options by volume and add metadata."""
    filtered = df[df["volume"] > MIN_VOLUME].copy()

    filtered["date"] = TODAY
    filtered["ticker"] = TICKER
    filtered["expiration"] = EXPIRATION
    filtered["optionType"] = option_type

    return filtered


# --------------------------------------------------
# Fetch Options Data
# --------------------------------------------------
ticker = yf.Ticker(TICKER)
EXPIRATION = get_nearest_expiration(ticker)

chain = ticker.option_chain(EXPIRATION)

calls = filter_options(chain.calls, "CALL")
puts = filter_options(chain.puts, "PUT")

# Combine calls + puts
all_options = pd.concat([calls, puts], ignore_index=True)

# Keep schema stable
COLUMNS = [
    "ticker",
    "date",
    "expiration",
    "optionType",
    "strike",
    "volume",
    "openInterest",
    "impliedVolatility",
    "lastPrice"
]

all_options = all_options[COLUMNS]

# --------------------------------------------------
# Save to CSV (Append Mode)
# --------------------------------------------------
if DATA_PATH.exists():
    existing = pd.read_csv(DATA_PATH)
    combined = pd.concat([existing, all_options], ignore_index=True)
else:
    combined = all_options

combined.to_csv(DATA_PATH, index=False)

# --------------------------------------------------
# Logging
# --------------------------------------------------
print(f"{TICKER} options scan completed for {TODAY}")
print(f"Expiration: {EXPIRATION}")
print("-" * 40)

print(f"Calls saved: {len(calls)}")
print(f"Call volume: {calls['volume'].sum()}")

print("-" * 40)

print(f"Puts saved: {len(puts)}")
print(f"Put volume: {puts['volume'].sum()}")
