from langchain.tools import tool
from configs.config import get_settings
from runs.database.db import connect_to_db
from runs.etl.pipeline import read


@tool
def get_yfinance_source_tool() -> str:
    """
    Retrieve the latest gold price data from the database and return it as a
    Markdown table. Returns the most recent rows (configurable via MAX_ROWS).

    The table schema includes: Date (index), Open, High, Low, Close, Adj Close, Volume.

    Returns:
        str: Markdown-formatted DataFrame, or a descriptive error message.
    """
    MAX_ROWS = 30

    try:
        with connect_to_db() as conn:
            df = read(conn, "gold_price")

        if df.empty:
            return "No gold price data found in the database."

        df = df.sort_index(ascending=False)[:MAX_ROWS]
        return df.to_markdown(index=True)

    except Exception as e:
        return f"Error retrieving gold price data: {e}"
