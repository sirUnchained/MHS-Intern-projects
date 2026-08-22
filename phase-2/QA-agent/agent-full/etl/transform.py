import pandas as pd


def transform(data: pd.DataFrame) -> pd.DataFrame:
    """
    Transform raw OHLCV data by flattening MultiIndex columns.

    Args:
        data: Raw DataFrame from Yahoo Finance with possible MultiIndex columns.

    Returns:
        DataFrame with flattened single-level column names.
    """

    if isinstance(data.columns, pd.MultiIndex):
        data.columns = [col[0] for col in data.columns]
        print("Flattened MultiIndex columns.")
    return data
