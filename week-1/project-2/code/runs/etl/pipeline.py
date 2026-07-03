import logging
import pandas as pd
import yfinance as yf
from sqlite3 import Connection
from typing import Literal

logger = logging.getLogger(__name__)


def extract(ticker: str, start_date: str, end_date: str = "today") -> pd.DataFrame:
    """
    Fetch OHLCV data from Yahoo Finance.

    Args:
        ticker: Yahoo symbol (e.g. 'GC=F').
        start_date: Start date in 'YYYY-MM-DD'.
        end_date: End date (defaults to today).

    Returns:
        DataFrame with DatetimeIndex, or empty DataFrame on failure.
    """
    try:
        begin = pd.to_datetime(start_date)
        end = pd.to_datetime(end_date)
    except Exception as e:
        raise ValueError(f"Invalid date format: {e}")

    logger.info(f"Downloading '{ticker}' from {start_date} to {end_date}")

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

        logger.info(f"Downloaded {len(data)} rows for '{ticker}'")
        return data

    except Exception as e:
        logger.error(f"Download failed: {e}")
        return pd.DataFrame()


def transform(data: pd.DataFrame) -> pd.DataFrame:
    """
    Flatten MultiIndex columns produced when downloading multiple tickers.
    Returns the DataFrame unchanged if columns are already flat.
    """
    if isinstance(data.columns, pd.MultiIndex):
        data.columns = [col[0] for col in data.columns]
        logger.info("Flattened MultiIndex columns.")
    return data


def load(
    data: pd.DataFrame,
    connection: Connection,
    table_name: str,
    if_exists: Literal["fail", "replace", "append"] = "fail",
) -> None:
    """
    Write DataFrame to a SQL table.

    Args:
        data: DataFrame with DatetimeIndex named 'Date'.
        connection: SQLite connection.
        table_name: Target table name.
        if_exists: Overwrite behaviour ('fail', 'replace', 'append').
    """
    if data.empty:
        logger.warning("Empty DataFrame — nothing written.")
        return

    df_to_write = data.reset_index()
    try:
        df_to_write.to_sql(
            name=table_name,
            con=connection,
            if_exists=if_exists,
            index=False,
            method="multi",
        )
        logger.info(f"Wrote {len(df_to_write)} rows to '{table_name}'")
    except Exception as e:
        logger.error(f"Write to '{table_name}' failed: {e}")
        raise


def read(connection: Connection, table_name: str) -> pd.DataFrame:
    """
    Read a table back as a DataFrame with DatetimeIndex.

    Args:
        connection: SQLite connection.
        table_name: Table name to read.

    Returns:
        DataFrame indexed by 'Date', or empty DataFrame on failure.
    """
    try:
        df = pd.read_sql(
            sql="SELECT * FROM gold_price",  # safe: table_name is internal only
            con=connection,
            parse_dates=["Date"],
            index_col="Date",
        )
        logger.info(f"Read {len(df)} rows from '{table_name}'")
        return df
    except Exception as e:
        logger.error(f"Read from '{table_name}' failed: {e}")
        return pd.DataFrame()


def run_pipeline(
    ticker: str,
    connection: Connection,
    table_name: str,
    start_date: str,
    end_date: str = "today",
    if_exists: Literal["fail", "replace", "append"] = "fail",
) -> pd.DataFrame:
    """
    Run the full extract → transform → load pipeline.

    Returns:
        The transformed DataFrame (for downstream use, e.g. charting).
    """
    raw = extract(ticker, start_date, end_date)
    if raw.empty:
        logger.warning("Pipeline stopped — no data to load.")
        return raw

    data = transform(raw)
    load(data, connection, table_name, if_exists)
    return data
