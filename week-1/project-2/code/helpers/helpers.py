import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.figure import Figure

import os


def plot_gold_prices(data: pd.DataFrame) -> Figure:
    """
    Plot the gold closing price over time.

    Args:
        data: DataFrame with a DatetimeIndex and a 'Close' column.

    Returns:
        Matplotlib Figure ready for st.pyplot().
    """
    fig, ax = plt.subplots(figsize=(10, 6))
    ax.plot(data["Close"], label="Gold Price (Close)", color="gold")
    ax.set_title("Gold Price Trend Over Time")
    ax.set_xlabel("Date")
    ax.set_ylabel("Price (USD)")
    ax.legend()
    ax.grid(True)
    fig.tight_layout()
    return fig


class Proxy:
    """Enable or disable an HTTP/HTTPS proxy via environment variables."""

    @staticmethod
    def enable(proxy_url: str) -> None:
        os.environ["http_proxy"] = proxy_url
        os.environ["https_proxy"] = proxy_url

    @staticmethod
    def disable() -> None:
        os.environ.pop("http_proxy", None)
        os.environ.pop("https_proxy", None)
