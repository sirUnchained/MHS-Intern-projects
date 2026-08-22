from langchain_tavily import TavilySearch
from app.core.config import get_settings


def get_search_tool():
    """Get our tavily search tool"""
    settings = get_settings()

    search_tool = TavilySearch(
        tavily_api_key=settings.TAVILY_API_KEY,  # API key for authenticating with Tavily service
        max_results=3,  # Limit search results to top 3 most relevant items for concise responses
        search_depth="fast",  # Use fast search depth for faster results
        topic="finance",  # Narrow search context to financial topics for better relevance
        include_raw_content=False,  # Exclude raw page content to reduce response size and API usage
    )

    return search_tool
