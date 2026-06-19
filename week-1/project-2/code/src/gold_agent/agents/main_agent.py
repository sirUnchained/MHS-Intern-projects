from langchain_groq import ChatGroq
from langchain_ollama import ChatOllama
from langgraph.checkpoint.memory import InMemorySaver
from configs.config import get_settings
from langchain.agents import create_agent

from src.gold_agent.tools.get_yfinance_source_tool import get_yfinance_source_tool
from src.gold_agent.tools.search_tool import get_search_tool
from prompt.prompt import system_prompt


def build_agent(checkpointer: InMemorySaver):
    """
    Builds and returns an agent.

    Args:
        checkpointer (InMemorySaver): The memory backend for conversation state.

    Returns:
        AgentExecutor: A compiled LangGraph agent ready for `.invoke()` calls.
    """

    settings = get_settings()

    if settings.LOCAL_MODEL:
        llm = ChatOllama(
            model="qwen2.5-1.5b-instruct:latest",
            temperature=settings.TEMPERATURE,
        )
    else:
        llm = ChatGroq(
            model="meta-llama/llama-4-scout-17b-16e-instruct",
            api_key=settings.GROQ_API_KEY,
            temperature=settings.TEMPERATURE,
        )

    search_tool = get_search_tool(settings.TAVILY_API_KEY)

    agent = create_agent(
        model=llm,
        tools=[get_yfinance_source_tool, search_tool],
        checkpointer=checkpointer,
        system_prompt=system_prompt,
    )

    return agent
