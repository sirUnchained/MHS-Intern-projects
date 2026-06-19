import os
from src.ETL.etl import read
from database.db import connect_to_db
import matplotlib.pyplot as plt

# you must configure it
PROXY_URL = "http://127.0.0.1:8889"


class Proxy:
    """This class can enable and disable proxy"""

    @staticmethod
    def enable_proxy() -> None:
        os.environ["http_proxy"] = PROXY_URL
        os.environ["https_proxy"] = PROXY_URL

    @staticmethod
    def disable_proxy() -> None:
        os.environ["http_proxy"] = ""
        os.environ["https_proxy"] = ""


def plot_gold_prices():
    """This function returns a plot uwing fetched data from yahoo finance."""
    with connect_to_db() as conn:
        data = read(conn, "gold_price")

    fig, ax = plt.subplots(figsize=(10, 6), ncols=1)
    ax.plot(data["Close"], label="Gold Price", color="gold")
    ax.set_title("Gold Price Trend Over Time")
    ax.set_xlabel("Date")
    ax.set_ylabel("Gold Price (USD)")
    ax.legend()
    ax.grid(True)
    fig.tight_layout()
    return fig
