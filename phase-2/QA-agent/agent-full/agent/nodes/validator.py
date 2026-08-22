from pydantic import BaseModel, Field
from typing import Optional
import regex as re
from langchain_core.messages import AIMessage

from agent.state import SupportState

PII_PATTERNS = {
    "SSN": r"\b\d{3}-\d{2}-\d{4}\b",
    "credit_card": r"\b(?:\d[ -]*?){13,16}\b",
    "email": r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b",
    "mobile": r"\b(?:\+\d{1,3}[- ]?)?\(?\d{3}\)?[- ]?\d{3}[- ]?\d{4}\b",
    "url": r"https?://(?:www\.)?[-\w@:%._\+~#=]{1,256}\.[a-zA-Z0-9()]{1,6}\b",
}


def main_agent_response_validator_node(state: SupportState):
    """
    Validate agent responses for PII (Personally Identifiable Information)
    before returning to the user. If sensitive data is detected, replaces
    the response with a fallback message.

    Args:
        state (SupportState): Conversation state containing the message history.
            The last message's text is checked against PII patterns.

    Returns:
        dict: State update containing:
            - "agent_response_validation": "good" if no PII found, "bad" otherwise
            - "messages": Updated message list with fallback response on failure

    Note:
        Uses PII_PATTERNS to detect sensitive data like emails, phone numbers,
        or SSNs to prevent accidental data leakage.
    """

    last_msg = state["messages"][-1].text

    # Validate agent response to detect any data which should not be
    for _, pattern in PII_PATTERNS.items():
        if re.search(pattern, last_msg, re.IGNORECASE):
            return {
                "messages": [
                    AIMessage(
                        content=f"Agent response was not valid, trying to generate a token for you."
                    )
                ],
                "agent_response_validation": "bad",
            }

    return {"agent_response_validation": "good"}


def main_agent_validation_route(state: SupportState):
    if "bad" in state["agent_response_validation"]:
        return "building_classifier_and_ticket_node"
    else:
        return "extract_data_after_agent_node"
