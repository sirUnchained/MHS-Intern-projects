from langchain_core.messages import HumanMessage
from agent.state import SupportState


def tool_limit_reached_node(state: SupportState):
    return {
        "messages": [
            HumanMessage(
                content=(
                    "Tool usage limit reached. You cannot call any more tools. Answer the user using existing information you already get."
                )
            )
        ]
    }
