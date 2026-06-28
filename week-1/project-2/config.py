import os
from dataclasses import dataclass
from dotenv import load_dotenv

load_dotenv()


@dataclass
class Settings:
    """
    Application settings loaded from environment variables.
    Required keys: GROK_API_KEY, TAVILY_API_KEY.
    All others have sensible defaults.
    """

    GROK_API_KEY: str = ""
    TAVILY_API_KEY: str = ""
    GROQ_MODEL_NAME: str = "meta-llama/llama-4-scout-17b-16e-instruct"
    MODEL_NAME: str = "qwen2.5-1.5b-instruct:latest"
    LOCAL_MODEL: bool = False
    USE_PROXY: bool = False
    PROXY_URL: str = "http://127.0.0.1:8889"
    DATABASE_PATH: str = "database/data.db"
    TEMPERATURE: float = 0.0
    TRICKER: str = "GC=F"

    def __post_init__(self):
        """Load from env and validate required keys."""
        self.GROK_API_KEY = os.getenv("GROK_API_KEY", "")
        self.TAVILY_API_KEY = os.getenv("TAVILY_API_KEY", "")
        self.GROQ_MODEL_NAME = os.getenv("GROQ_MODEL_NAME", self.GROQ_MODEL_NAME)
        self.MODEL_NAME = os.getenv("MODEL_NAME", self.MODEL_NAME)
        self.LOCAL_MODEL = os.getenv("LOCAL_MODEL", "false").lower() in (
            "true",
            "1",
            "yes",
        )
        self.USE_PROXY = os.getenv("USE_PROXY", "false").lower() in ("true", "1", "yes")
        self.PROXY_URL = os.getenv("PROXY_URL", self.PROXY_URL)
        self.DATABASE_PATH = os.getenv("DATABASE_PATH", self.DATABASE_PATH)
        self.TEMPERATURE = float(os.getenv("TEMPERATURE", "0.0"))
        self.TRICKER = os.getenv("TRICKER", self.TRICKER)

        if not self.GROK_API_KEY:
            raise ValueError("GROK_API_KEY must be set in environment or .env")
        if not self.TAVILY_API_KEY:
            raise ValueError("TAVILY_API_KEY must be set in environment or .env")


# Singleton instance (cached)
_settings: Settings | None = None


def get_settings() -> Settings:
    """Return the cached Settings instance."""
    global _settings
    if _settings is None:
        _settings = Settings()
    return _settings
