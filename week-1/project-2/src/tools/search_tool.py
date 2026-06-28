from langchain_tavily import TavilySearch
from configs.config import get_settings


def get_search_tool():
    """Return a Tavily web search tool configured for financial news."""
    settings = get_settings()
    return TavilySearch(
        tavily_api_key=settings.TAVILY_API_KEY,
        max_results=3,
        search_depth="basic",
        topic="finance",
        include_raw_content=False,
    )
