import logging
import pandas as pd
import yfinance as yf
from sqlite3 import Connection
from typing import Literal

logger = logging.getLogger(__name__)


def extract(
    ticker: str,
    start_date: str,
    end_date: str = "today",
) -> pd.DataFrame:
    """
    Fetch Yahoo Finance data.

    Args:
        ticker: Yahoo symbol (e.g., 'AAPL', 'GC=F').
        start_date: Start date in 'YYYY-MM-DD'.
        end_date: End date (defaults to today).

    Returns:
        DataFrame with a DatetimeIndex named 'Date' (or empty on failure).
    """

    # Simple validation for `start_date` and `end_date`
    try:
        begin = pd.to_datetime(start_date)
        end = pd.to_datetime(end_date)
    except Exception as e:
        raise ValueError(f"Invalid date format: {e}")

    logger.info(f"Downloading '{ticker}' from {start_date} to {end_date or 'today'}")

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
            logger.warning(f"No data for '{ticker}' in that range.")
            return pd.DataFrame()
        else:
            logger.info(f"Downloaded {len(data)} rows for '{ticker}'")
            return data

    except Exception as e:
        logger.error(f"Download failed: {e}")
        return pd.DataFrame()


def transform(data: pd.DataFrame) -> pd.DataFrame:
    """
    Flatten MultiIndex columns (from downloading multiple tickers)
    by taking only the first level.

    If columns are already flat, returns the DataFrame unchanged.
    """
    if isinstance(data.columns, pd.MultiIndex):
        data.columns = [col[0] for col in data.columns]
        logger.info("Flattened MultiIndex columns to single level.")

    return data


def load(
    data: pd.DataFrame,
    connection: Connection,
    table_name: str,
    if_exists: Literal["fail", "replace", "append"] = "fail",
) -> None:
    """
    Write the DataFrame to a SQL table.

    The DatetimeIndex (named 'Date') is written as a regular column
    so it can be restored on read.

    Args:
        data: DataFrame with a DatetimeIndex.
        connection: SQLite connection object.
        table_name: Target table name.
        if_exists: 'fail', 'replace', or 'append'.
    """
    if data.empty:
        logger.warning("Empty DataFrame – nothing written.")
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


def read(
    connection: Connection,
    table_name: str,
) -> pd.DataFrame:
    """
    Read the table back as a DataFrame with DatetimeIndex.

    Args:
        connection: SQLite connection object.
        table_name: Name of the table.

    Returns:
        DataFrame with index set to the 'Date' column (parsed as datetime).
    """
    try:
        df = pd.read_sql(
            sql=f"SELECT * FROM {table_name}",
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
    Execute extract → transform → load.

    Args:
        ticker: Yahoo symbol.
        connection: SQLite connection object.
        table_name: Target SQL table.
        start_date: Start date.
        end_date: End date.
        if_exists: Table overwrite behaviour.

    Returns:
        The extracted DataFrame (for inspection).
    """
    raw = extract(ticker, start_date, end_date)
    if not raw.empty:
        data = transform(raw)
        load(data, connection, table_name, if_exists)
    else:
        logger.warning("Pipeline stopped – no data to load.")
    return raw
