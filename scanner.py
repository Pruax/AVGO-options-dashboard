from datetime import datetime, date
from pathlib import Path

import pandas as pd
import yfinance as yf

# --------------------------------------------------
# Configuration
# --------------------------------------------------
TICKER = "AVGO"
MIN_VOLUME = 500

DATA_PATH = Path("C:/Users/B Dog/Documents/options_scanner/avgo_options.csv")

# --------------------------------------------------
# Helpers
# --------------------------------------------------
def get_nearest_expiration(ticker: yf.Ticker) -> str:
    """Return the nearest non-expired option expiration."""
    
    today = date.today()
    
    expirations = [
        exp for exp in ticker.options
        if datetime.strptime(exp, "%Y-%m-%d").date() >= today
    ]

    return min(
        expirations,
        key=lambda x: datetime.strptime(x, "%Y-%m-%d").date()
    )


def filter_options(df: pd.DataFrame, option_type: str, expiration: str, 
                    min_volume: int, meta: dict) -> pd.DataFrame:
    """Filter options by volume and add metadata."""
    
    filtered = df[df["volume"] > min_volume].copy()

    filtered["date"] = meta["today"]
    filtered["scan_time"] = meta["scan_time"]
    filtered["ticker"] = meta["ticker"]
    filtered["expiration"] = expiration
    filtered["optionType"] = option_type

    return filtered

# --------------------------------------------------
# Create scanner_log file
# --------------------------------------------------
LOG_FILE = Path(__file__).parent / "scanner_log.txt"

def log(message: str):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    LOG_FILE.parent.mkdir(parents=True, exist_ok=True)

    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(f"[{timestamp}] {message}\n")
        
def run_scan():
    log("Scan started")

    try:
        # --------------------------------------------------
        # Fetch Options Data
        # --------------------------------------------------
        now = datetime.now()
        
        meta = {
            "ticker": TICKER,
            "today": now.date().isoformat(),
            "scan_time": now.strftime("%Y-%m-%d %H:%M:%S")
        }

        ticker = yf.Ticker(TICKER)
        expiration = get_nearest_expiration(ticker)
        
        
        chain = ticker.option_chain(expiration)

        calls = filter_options(chain.calls, "CALL", expiration, MIN_VOLUME, meta)
        puts = filter_options(chain.puts, "PUT", expiration, MIN_VOLUME, meta)

        # Combine calls + puts
        all_options = pd.concat([calls, puts], ignore_index=True)

        # Keep schema stable
        COLUMNS = [
            "ticker",
            "date",
            "scan_time",
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

            combined = pd.concat(
                [existing, all_options],
                ignore_index=True
            )
        else:
            combined = all_options

        combined = combined.drop_duplicates(
            subset=[
                "ticker",
                "expiration",
                "strike",
                "optionType",
                "scan_time"
            ],
            keep="last"
        )

        combined.to_csv(DATA_PATH, index=False)

        # --------------------------------------------------
        # Logging
        # --------------------------------------------------
        log(f"{TICKER} scan completed for {meta['scan_time']}")
        log(f"Expiration: {expiration}")
        
        log(f"-" * 40)

        log(f"Calls saved: {len(calls)}")
        log(f"Call volume: {calls['volume'].sum()}")
        
        log(f"-" * 40)

        log(f"Puts saved: {len(puts)}")
        log(f"Put volume: {puts['volume'].sum()}")
        
        log(f"-" * 20)

        log("Scan completed successfully")

    except Exception as e:
        log(f"ERROR: {str(e)}")
        raise
        
if __name__ == "__main__":
    run_scan()