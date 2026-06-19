from langchain.tools import tool
import pandas as pd
from src.ETL.etl import read
from database.db import connect_to_db


@tool
def get_yfinance_source_tool() -> str:
    """
    Retrieve the latest gold price data from the database and return it as a Markdown table.

    The expected table schema (from the ETL pipeline) includes:
        - Index: Date (datetime)
        - Columns: Open, High, Low, Close, Adj Close, Volume (all numeric)

    Returns:
        str: A Markdown-formatted string representation of the DataFrame. If the table
            is empty or the read fails, returns an empty string (or a descriptive
            message – adjust as needed for your tool).

    Raises:
        Exception: The tool catches any database/connection errors internally and returns
                an empty string to avoid breaking the agent, but you may choose to
                re‑raise if failure should be propagated.

    Notes:
        - This tool assumes the database connection is configured correctly and that
        the `gold_price` table exists (it should be created by running the ETL pipeline).
        - If you need data for a different ticker, consider creating a parameterized version
        of this tool.
    """

    try:
        with connect_to_db() as conn:
            # Read the entire table
            df = read(conn, "gold_price")

        if df.empty:
            return "No gold price data found in the database."

        # sort it from newest to oldest, I also select first 30 row
        # for not filling LLM context with these datas
        df = df.sort_index(ascending=False)[:30]

        # Convert to markdown for LLM readability
        return df.to_markdown(index=False)

    except Exception as e:
        # Return the error for LLM
        return f"Error retrieving gold price data: {e}"
