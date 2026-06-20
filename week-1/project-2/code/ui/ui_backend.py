import streamlit as st
from database.db import connect_to_db
from src.ETL.etl import run_pipeline
from configs.config import get_settings
from helpers.helpers import Proxy


def setup_backend():
    """
    Run the ETL pipeline and enable the proxy. This function runs every time user
    requests for showing uptodate data.

    Returns:
        DataFrame containing the gold price data, with 'Date' as DatetimeIndex.
    """

    settings = get_settings()

    with connect_to_db() as conn:
        data = run_pipeline(
            ticker=settings.TRICKER,
            connection=conn,
            table_name="gold_price",
            start_date="2025-01-01",
            if_exists="replace",
        )

    # Enable proxy
    if settings.USE_PROXY:
        Proxy.enable_proxy()

    return data
