import os
from dotenv import load_dotenv
from src.state import BuildingInfo

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

    OLLAMA_MODEL_NAME: str = os.getenv("OLLAMA_MODEL_NAME", "qwen2.5-1.5b-instruct")
    OLLAMA_EMBEDDING_MODEL_NAME: str = os.getenv("OLLAMA_EMBEDDING_MODEL_NAME")

    GOOGLE_API_KEY: str = os.getenv("GOOGLE_API_KEY")
    GOOGLE_MODEL_NAME: str = os.getenv("GOOGLE_MODEL_NAME", "qwen2.5-1.5b-instruct")

    POSTGRESQL_DATABASE_LINK: str = os.getenv(
        "POSTGRESQL_DATABASE_LINK", "INVALID_LINK"
    )

    TAVILY_API_KEY: str = os.getenv("TAVILY_API_KEY")

    MAX_TOOL_CALLS: int = int(os.getenv("MAX_TOOL_CALLS", "5"))

    IS_DEVELOPMENT: bool = os.getenv("IS_DEVELOPMENT", "true").lower() == "true"
    USE_PROXY: bool = os.getenv("USE_PROXY", "false").lower() == "true"
    PROXY_LINK: str = os.getenv("PROXY_LINK")


_settings = None


def get_settings() -> Settings:
    global _settings
    if _settings is None:
        _settings = Settings()
    return _settings


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
