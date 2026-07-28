import pandas as pd
import yfinance as yf


def extract(ticker: str, start_date: str, end_date: str = "today") -> pd.DataFrame:
    """Fetch OHLCV data from Yahoo Finance."""
    try:
        begin = pd.to_datetime(start_date)
        end = pd.to_datetime(end_date)
    except Exception as e:
        raise ValueError(f"Invalid date format: {e}")

    try:
        data = yf.download(
            tickers=ticker,
            start=begin,
            end=end,
            progress=False,
            auto_adjust=False,
            threads=True,
        )
        if data is None or data.empty:
            raise RuntimeError(f"No data returned for '{ticker}'.")

        print(f"Downloaded {len(data)} rows for '{ticker}'")
        return data
    except Exception as e:
        print(f"Download failed: {e}")
        return pd.DataFrame()
