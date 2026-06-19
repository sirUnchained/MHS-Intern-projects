from langchain_tavily import TavilySearch


def get_search_tool(TAVILY_API_KEY: str):
    """
    This function returns search tool using tavily ai.
    """
    return TavilySearch(
        tavily_api_key=TAVILY_API_KEY,
        max_results=3,  # I use free plan so I must use 3
        search_depth="basic",  # I use free plan so I must use it
        topic="finance",  # prioritize financial news sources (Bloomberg, Yahoo finance, etc.)
        include_raw_content=False,  # omit full text, saves free plan
    )
