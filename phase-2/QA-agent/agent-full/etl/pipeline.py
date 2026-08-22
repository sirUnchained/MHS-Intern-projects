import pandas as pd
from sqlalchemy.engine import Engine
from typing import Literal
from etl.extract import extract
from etl.transform import transform
from etl.load import load


def run_pipeline(
    ticker: str,
    engine: Engine,
    table_name: str,
    start_date: str,
    end_date: str = "today",
    if_exists: Literal["fail", "replace", "append"] = "fail",
    add_vector_column: bool = True,
) -> pd.DataFrame:
    """
    Run the full extract → transform → load pipeline.

    Args:
        ticker: Stock ticker symbol to fetch data for (e.g., 'AAPL').
        engine: SQLAlchemy database engine for connecting to the target database.
        table_name: Name of the database table to write the data to.
        start_date: Start date for data extraction (format: 'YYYY-MM-DD').
        end_date: End date for data extraction (format: 'YYYY-MM-DD' or 'today' for current date).
            Defaults to "today".
        if_exists: Action to take if the table already exists:
            - 'fail': Raise an error.
            - 'replace': Drop and recreate the table.
            - 'append': Insert new rows into the existing table.
            Defaults to "fail".
        add_vector_column: If True, adds a vectorized representation column to the data
            before loading (useful for ML applications). Defaults to True.

    Returns:
        The transformed DataFrame (for downstream use, e.g. charting).
    """

    raw = extract(ticker, start_date, end_date)
    if raw.empty:
        print("Pipeline stopped — no data to load.")
        return raw

    data = transform(raw)
    load(data, engine, table_name, if_exists, add_vector_column)
    return data
