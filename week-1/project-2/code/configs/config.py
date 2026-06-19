import os
from dotenv import load_dotenv

load_dotenv()


class Settings:
    """
    Application settings from environment variables.
    Required keys: GROQ_API_KEY, TAVILY_API_KEY.
    All others have sensible defaults.
    """

    # Required (will raise error if missing)
    TRICKER: str = os.getenv("TRICKER")
    GROQ_API_KEY: str = os.getenv("GROQ_API_KEY")
    TAVILY_API_KEY: str = os.getenv("TAVILY_API_KEY")
    LOCAL_MODEL: bool = os.getenv("LOCAL_MODEL", "false").lower() in (
        "true",
        "1",
        "yes",
    )
    DATABASE_PATH: str = os.getenv("DATABASE_PATH")
    MODEL_NAME: str = os.getenv("MODEL_NAME")
    TEMPERATURE: float = float(os.getenv("TEMPERATURE", "0.0"))

    def __post_init__(self):
        """Check that required keys are present."""
        if not self.GROQ_API_KEY:
            raise ValueError("GROQ_API_KEY must be set in environment or .env")
        if not self.TAVILY_API_KEY:
            raise ValueError("TAVILY_API_KEY must be set in environment or .env")


# Singleton instance (cached)
_settings = None


def get_settings() -> Settings:
    """Return the cached Settings instance."""
    global _settings
    if _settings is None:
        _settings = Settings()
    return _settings
