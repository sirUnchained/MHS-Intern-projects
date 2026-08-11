import asyncio
import logging
from datetime import datetime, timedelta, timezone

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger

from app.core.config import get_settings, ASSET_TICKERS
from app.core.engine import get_engine
from etl.pipeline import run_pipeline

logger = logging.getLogger("etl.scheduler")

_scheduler: AsyncIOScheduler | None = None


def refresh_all_market_data() -> None:
    """
    Blocking call that re-downloads OHLCV history for every asset in
    ASSET_TICKERS and replaces the corresponding `ohlcv_<asset>` table.

    Synchronous on purpose (yfinance/pandas/SQLAlchemy are all sync under
    the hood) — always invoke this via asyncio.to_thread(...) from async
    code so it doesn't block the event loop.
    """
    settings = get_settings()
    engine = get_engine()
    start_date = (
        datetime.now(timezone.utc) - timedelta(days=settings.MARKET_DATA_LOOKBACK_DAYS)
    ).strftime("%Y-%m-%d")

    for asset, ticker in ASSET_TICKERS.items():
        table_name = f"ohlcv_{asset}"
        try:
            logger.info(
                f"[market-data] refreshing '{asset}' ({ticker}) -> {table_name}"
            )
            run_pipeline(
                ticker=ticker,
                engine=engine,
                table_name=table_name,
                start_date=start_date,
                if_exists="replace",
                add_vector_column=True,
            )
        except Exception as e:
            # One failing asset (rate limit, bad ticker, network blip)
            # shouldn't stop the rest of the assets from refreshing.
            logger.error(f"[market-data] failed to refresh '{asset}': {e}")


async def refresh_all_market_data_async() -> None:
    """Async wrapper so this can be awaited/scheduled from asyncio code."""
    await asyncio.to_thread(refresh_all_market_data)


def start_scheduler() -> AsyncIOScheduler:
    """
    Creates and starts the AsyncIOScheduler with a single daily job.
    Call once from the app's lifespan startup — pair with stop_scheduler()
    on shutdown.
    """
    global _scheduler
    settings = get_settings()

    scheduler = AsyncIOScheduler(timezone="UTC")
    scheduler.add_job(
        refresh_all_market_data_async,
        trigger=CronTrigger(
            hour=settings.MARKET_DATA_REFRESH_HOUR_UTC,
            minute=settings.MARKET_DATA_REFRESH_MINUTE_UTC,
        ),
        id="daily_market_data_refresh",
        replace_existing=True,
        misfire_grace_time=3600,  # if the app was down at the scheduled time, still run within 1h of restart
    )
    scheduler.start()
    _scheduler = scheduler
    logger.info(
        "[market-data] scheduler started — daily refresh at "
        f"{settings.MARKET_DATA_REFRESH_HOUR_UTC:02d}:{settings.MARKET_DATA_REFRESH_MINUTE_UTC:02d} UTC"
    )
    return scheduler


def stop_scheduler() -> None:
    global _scheduler
    if _scheduler is not None:
        _scheduler.shutdown(wait=False)
        _scheduler = None
