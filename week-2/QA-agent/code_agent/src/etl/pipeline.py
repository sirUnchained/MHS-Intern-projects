import pandas as pd
from sqlalchemy.engine import Engine
from typing import Literal
from src.etl.extract import extract
from src.etl.transform import transform
from src.etl.load import load


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
