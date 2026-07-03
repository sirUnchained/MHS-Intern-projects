from langchain_groq import ChatGroq
from langchain_ollama import ChatOllama

from langgraph.prebuilt import create_react_agent
from langgraph.checkpoint.memory import InMemorySaver

from configs.config import get_settings

from prompts.prompt import system_prompt

from src.tools.yfinance_tool import get_yfinance_source_tool
from src.tools.search_tool import get_search_tool


def build_gold_agent(checkpointer: InMemorySaver):
    """
    Build and return a LangGraph ReAct agent.

    Args:
        checkpointer: Memory backend for persisting conversation state per thread.

    Returns:
        A compiled LangGraph agent ready for `.invoke()` calls.
    """
    settings = get_settings()

    if settings.LOCAL_MODEL:
        llm = ChatOllama(
            model=settings.MODEL_NAME,
            temperature=settings.TEMPERATURE,
        )
    else:
        llm = ChatGroq(
            model=settings.GROQ_MODEL_NAME,
            api_key=settings.GROK_API_KEY,  # type: ignore
            temperature=settings.TEMPERATURE,
        )

    search_tool = get_search_tool()

    agent = create_react_agent(
        model=llm,
        tools=[get_yfinance_source_tool, search_tool],
        checkpointer=checkpointer,
        prompt=system_prompt,
    )

    return agent
