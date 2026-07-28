import pandas as pd


def transform(data: pd.DataFrame) -> pd.DataFrame:
    """Flatten MultiIndex columns (if any)."""
    if isinstance(data.columns, pd.MultiIndex):
        data.columns = [col[0] for col in data.columns]
        print("Flattened MultiIndex columns.")
    return data
