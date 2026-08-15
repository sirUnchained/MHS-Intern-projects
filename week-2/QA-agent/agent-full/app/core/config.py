import os
from dotenv import load_dotenv
from agent.state import BuildingInfo

from dotenv import load_dotenv
from pathlib import Path

load_dotenv(".env")


class Settings:
    """Application settings loaded from environment variables."""

    GROQ_API_KEY: str = os.getenv("GROQ_API_KEY")
    GROQ_MODEL_NAME: str = os.getenv("GROQ_MODEL_NAME", "openai/gpt-oss-20b")
    GROQ_CLASSIFY_MODEL_NAME: str = os.getenv(
        "GROQ_CLASSIFY_MODEL_NAME", "meta/llama-3.1-8b-instant"
    )

    GOOGLE_API_KEY: str = os.getenv("GOOGLE_API_KEY")
    GOOGLE_MODEL_NAME: str = os.getenv("GOOGLE_MODEL_NAME", "qwen2.5-1.5b-instruct")
    GOOGLE_EMBEDDING_MODEL_NAME: str = os.getenv("GOOGLE_EMBEDDING_MODEL_NAME")

    POSTGRESQL_DATABASE_LINK: str = os.getenv(
        "POSTGRESQL_DATABASE_LINK", "INVALID_LINK"
    )

    TAVILY_API_KEY: str = os.getenv("TAVILY_API_KEY")

    MARKET_DATA_LOOKBACK_DAYS: int = int(os.getenv("MARKET_DATA_LOOKBACK_DAYS", "1825"))
    MARKET_DATA_REFRESH_HOUR_UTC: int = int(
        os.getenv("MARKET_DATA_REFRESH_HOUR_UTC", "10")
    )
    MARKET_DATA_REFRESH_MINUTE_UTC: int = int(
        os.getenv("MARKET_DATA_REFRESH_MINUTE_UTC", "0")
    )

    MAX_TOOL_CALLS: int = int(os.getenv("MAX_TOOL_CALLS", "5"))

    IS_DEVELOPMENT: bool = os.getenv("IS_DEVELOPMENT", "true").lower() == "true"
    USE_PROXY: bool = os.getenv("USE_PROXY", "false").lower() == "true"
    PROXY_LINK: str = os.getenv("PROXY_LINK")

    JWT_SECRET: str = os.getenv("JWT_SECRET")

    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")


# Current support buildings
SUPPORT_BUILDINGS: list[BuildingInfo] = [
    {
        "name": "Building finance - Billing & Payments",
        "phone": "+98-21-0000-0001",
        "services": ["billing", "invoices", "refunds", "payment disputes"],
    },
    {
        "name": "Building software - Technical Support",
        "phone": "+98-21-0000-0002",
        "services": ["bugs", "product issues", "installation", "outages"],
    },
    {
        "name": "Building general - General Reception",
        "phone": "+98-21-0000-0004",
        "services": ["general inquiries", "anything not covered elsewhere"],
    },
]
# Ticker used for each asset the ETL pipeline knows how to fetch.
ASSET_TICKERS: dict[str, str] = {
    "gold": "GC=F",
    "dxy": "DX-Y.NYB",
    "silver": "SI=F",
    "oil": "CL=F",
    "sp500": "^GSPC",
}
_settings = None


def get_settings() -> Settings:
    global _settings
    if _settings is None:
        _settings = Settings()
    return _settings
