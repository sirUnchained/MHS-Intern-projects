from langchain.tools import tool
from src.helpers import get_engine
from src.etl.read import read


def get_financial_data_tool():
    @tool
    def financial_data_tool(
        asset: str = "gold", max_rows: int = 30, include_stats: bool = True
    ) -> str:
        """
        Retrieve the latest OHLCV data for a given asset from the database. Optionally include a statistical summary of the price history.
        Use this tool whenever user ask about 'gold','dxy','silver','oil','sp500' price.
        Example:
        - How much gold price changed during last week?
            - You must call this tool with asset="gold" and max_rows="7".

        Args:
            asset: Asset name (table suffix). Options: 'gold','dxy','silver','oil','sp500'.
            max_rows: Number of most recent rows to display in the table and each row has data of a day (default 30).
            include_stats: If True, include a statistical summary section (default True).

        Returns:
            str: Markdown-formatted output with a data table and statistical analysis.
        """

        table_name = f"ohlcv_{asset}"
        try:
            # Read data from database
            engine = get_engine()
            df = read(engine, table_name)
            if df.empty:
                return f"No data for {asset}."

            # Choose the best closing price column
            price_col = "adj_close" if "adj_close" in df.columns else "close"
            prices = df[price_col]

            # ----- Recent prices (most recent `max_rows`) -----
            recent_prices = prices.tail(max_rows)
            lines = [f"Recent {asset.upper()} prices:"]
            for date, val in recent_prices.items():
                lines.append(f"  {date.strftime('%Y-%m-%d')}: {val:.2f}")

            # ----- 1‑day change (from previous day to latest) -----
            latest = prices.iloc[-1]
            previous = prices.iloc[-2] if len(prices) > 1 else latest
            change_abs = latest - previous
            change_pct = (change_abs / previous) * 100 if previous != 0 else 0

            # ----- Statistical summary (if llm choses) -----
            if include_stats:
                # Annualised volatility (using last 30 trading days)
                if len(prices) >= 30:
                    daily_returns = prices.pct_change().dropna().tail(30)
                    annual_vol = daily_returns.std() * (
                        252**0.5
                    )  # annualised standard deviation
                    vol_str = f"{annual_vol:.1f}%"
                else:
                    vol_str = "N/A"

                # Descriptive statistics (full history)
                stats = {
                    "Mean": prices.mean(),
                    "Median": prices.median(),
                    "Std Dev": prices.std(),
                    "Min": prices.min(),
                    "Max": prices.max(),
                    "25th %": prices.quantile(0.25),
                    "75th %": prices.quantile(0.75),
                }

                lines.append("\nStatistics (full history):")
                for label, val in stats.items():
                    lines.append(f"  {label}: {val:.2f}")

                lines.append(f"\nCurrent price: {latest:.2f}")
                lines.append(f"Change (1 day): {change_abs:+.2f} ({change_pct:+.1f}%)")
                lines.append(f"Annualized volatility (30d): {vol_str}")

            return "\n".join(lines)

        except Exception as e:
            return f"Error: {e}"

    return financial_data_tool
