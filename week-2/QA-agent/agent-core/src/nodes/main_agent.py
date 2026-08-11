from langchain_core.messages import SystemMessage
from langgraph.store.base import BaseStore

from src.tools.financial_data_tool import get_financial_data_tool
from src.tools.search_tool import get_search_tool
from src.tools.retriever_tool import get_retriever_tool
from src.state import SupportState
from src.prompts import MAIN_AGENT_SYSTEM_PROMPT
from config import get_settings


def get_main_agent_node(llm, embedding_llm):
    tools = [
        get_financial_data_tool(),
        get_retriever_tool(embedding_llm),
        get_search_tool(),
    ]

    def main_agent_node(state: SupportState, *, store: BaseStore) -> dict:
        user_id = state["user_id"]
        namespace = ("memories", user_id)

        # semantic search over past memories relevant to the latest message
        messages = state.get("messages", [])
        if not messages:
            return {"messages": []}

        # get users last message, if there is nothing then dont continue
        last_user_msg = next((m for m in reversed(messages) if m.type == "human"), None)
        if last_user_msg is None:
            return {"messages": []}

        # Search into our history using user lastest message
        relevant_memories = store.search(namespace, query=last_user_msg.text, limit=3)
        memory_lines = []
        for item in relevant_memories:
            value = item.value
            summary = value.get("summary")
            if not summary:
                continue
            date = value.get("created_at", "")[:10]
            memory_lines.append(f"- ({date}, relevance {item.score:.2f}) {summary}")

        # Build a compact context block
        memory_context = "\n".join(memory_lines) if memory_lines else ""

        # prepend system prompt so the LLM knows its role
        system_content = MAIN_AGENT_SYSTEM_PROMPT
        if memory_context:
            system_content = "\n\n # HISTORY CHAT\n" + memory_context
            # print(f"SYSTEM CONTET WITH MEMORY:\n {system_content}")

        final_messages = [SystemMessage(content=system_content)]

        # Remove any existing SystemMessages because we want to append new system message
        filtered_messages = [
            msg for msg in messages if not isinstance(msg, SystemMessage)
        ]

        llm_with_tools = llm.bind_tools(tools)
        response = llm_with_tools.invoke(final_messages + filtered_messages)

        return {
            "messages": [response],
            "tool_calls_count": state.get("tool_calls_count", 0)
            + (1 if getattr(response, "tool_calls", None) else 0),
        }

    return main_agent_node


def main_agent_route(state: SupportState):
    last_msg = state["messages"][-1]

    settings = get_settings()
    if state.get("tool_calls_count", 0) >= settings.MAX_TOOL_CALLS:
        return "tool_limit_reached_node"

    if getattr(last_msg, "tool_calls", None):
        return "tools"

    return "main_agent_response_validator_node"
