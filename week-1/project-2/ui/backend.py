import streamlit as st
import pandas as pd
from runs.database.db import connect_to_db
from runs.etl.pipeline import run_pipeline
from configs.config import get_settings
from helpers.helpers import Proxy


@st.cache_data(ttl=3600, show_spinner="Fetching latest gold prices...")
def setup_backend() -> pd.DataFrame:
    """
    Run the ETL pipeline and return the gold price DataFrame.

    Cached for 1 hour — avoids hammering Yahoo Finance on every page reload.
    Force a refresh by calling st.cache_data.clear() or restarting the app.

    Returns:
        DataFrame containing gold price data with 'Date' as DatetimeIndex.
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

    if settings.USE_PROXY:
        Proxy.enable(settings.PROXY_URL)

    return data
