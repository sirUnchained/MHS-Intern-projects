from typing import TypedDict, Literal, Optional
from typing import Annotated
from operator import add
from langchain_core.messages import BaseMessage
from langchain_core.documents import Document


class BuildingInfo(TypedDict):
    """Support building/department the user can be routed to."""

    name: str
    phone: str
    services: list[str]


class UserTicketData(TypedDict):
    """User information extracted from the conversation."""

    building: str
    topic: str
    budget: str
    job: str
    goals: str
    phone: str
    services: list[str]


class SupportState(TypedDict, total=False):
    """
    Shared state passed between graph nodes.
    total=False because not every field exists at every step.
    """

    # All messages in a loop of graph
    messages: Annotated[list[BaseMessage], add]

    # User ID
    user_id: str

    # Data for Escalation branch
    new_ticket: Optional[UserTicketData]

    # Router decision
    route: Literal["rag", "escalate"]
    agent_response_validation: Literal["good", "bad"]

    # RAG branch
    documents: list[Document]
    retry_count: int

    # All tool calls limit
    tool_calls_count: int

    # Final output
    final_answer: str
