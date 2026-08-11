from pydantic import BaseModel, Field
from typing import Optional
import regex as re
from langchain_core.messages import AIMessage

from src.state import SupportState


class ValidationResult(BaseModel):
    result: str = Field(
        'If the response contains **hallucinations** or **PII** then this field is **"bad"**\nElse this filed is **"good**"'
    )
    answer: Optional[str] = Field(
        "If you chose **bad** tell user with respect that you should redirect the conversation to supports and tell the reason, else put this field empty."
    )


PII_PATTERNS = {
    "SSN": r"\b\d{3}-\d{2}-\d{4}\b",
    "credit_card": r"\b(?:\d[ -]*?){13,16}\b",
    "email": r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b",
    "mobile": r"\b(?:\+\d{1,3}[- ]?)?\(?\d{3}\)?[- ]?\d{3}[- ]?\d{4}\b",
    "url": r"https?://(?:www\.)?[-\w@:%._\+~#=]{1,256}\.[a-zA-Z0-9()]{1,6}\b",
}


def main_agent_response_validator_node(state: SupportState):
    """Validate main agent response node"""

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
