import streamlit as st
from database.db import connect_to_db
from src.ETL.etl import run_pipeline
from configs.config import get_settings
from utils.utils import Proxy


def setup_backend():
    """
    Run the ETL pipeline (only if the gold_price table is empty)
    and enable the proxy.
    This function is cached to run only once per Streamlit session.
    """
    settings = get_settings()

    # Check if gold_price table already has data
    with connect_to_db() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM gold_price")
        count = cursor.fetchone()[0]

    if count == 0:
        with connect_to_db() as conn:
            run_pipeline(
                ticker=settings.TRICKER,
                connection=conn,
                table_name="gold_price",
                start_date="2025-01-01",
                if_exists="replace",
            )

    # Enable proxy
    if settings.USE_PROXY:
        Proxy.enable_proxy()
