from pydantic import BaseModel, Field
import uuid
from datetime import datetime, timezone
from typing import Literal
from langchain_core.messages import HumanMessage, SystemMessage
from langgraph.store.base import BaseStore

from helpers import safe_structured_invoke
from src.state import SupportState
from src.prompts import DATA_EXTRACTION_FOR_DATABASE_SYSTEM_PROMPT


class MemoryRecord(BaseModel):
    user_id: str
    message_id: str
    agent_response: str
    summary: str | None
    category: str
    topic: str | None
    budget: str | None
    job: str | None
    goals: str | None
    user_mark: int = Field(default=3, ge=1, le=5)
    created_at: str


class ExtractedFact(BaseModel):
    should_save: bool = Field(
        description="True only if this exchange contains something worth remembering long-term"
    )
    summary: str | None = Field(
        default=None,
        description="Short summary of what the user was asking/talking about. None if not worth saving or should be escalated to support team as-is.",
    )
    category: Literal[
        "preference", "building_info", "billing", "budget", "job", "goal", "other"
    ] = "other"
    topic: str | None = None
    budget: str | None = None
    job: str | None = None
    goals: str | None = None


def get_extract_data_after_agent_node(llm):
    def extract_data_after_agent_node(state: SupportState, *, store: BaseStore):
        messages = state["messages"]
        last_human_msg = next(
            (m for m in reversed(messages) if m.type == "human"), None
        )
        last_ai_msg = next(
            (m for m in reversed(messages) if m.type == "ai" and m.text), None
        )

        # If there is no last Ai message or it's less than 50 words, just eixit the node
        if (
            not last_human_msg
            or not last_ai_msg
            or len(last_ai_msg.text.split(" ")) < 50
        ):
            return {}

        convo_text = f"User: {last_human_msg.text}\nAgent: {last_ai_msg.text}"

        extractor_llm = llm.with_structured_output(ExtractedFact)
        extracted = safe_structured_invoke(
            extractor_llm,
            [
                SystemMessage(content=DATA_EXTRACTION_FOR_DATABASE_SYSTEM_PROMPT),
                HumanMessage(content=convo_text),
            ],
            fallback=ExtractedFact(should_save=False),
        )

        # If LLM choses that these data worth not to save, just exit
        if not extracted.should_save:
            return {}

        # Generate a new record and save in database
        record = MemoryRecord(
            user_id=state["user_id"],
            message_id=str(uuid.uuid4()),
            agent_response=last_ai_msg.text,
            summary=extracted.summary,
            category=extracted.category,
            topic=extracted.topic,
            budget=extracted.budget,
            job=extracted.job,
            goals=extracted.goals,
            created_at=datetime.now(timezone.utc).isoformat(),
        )

        store.put(
            ("memories", state["user_id"]),
            key=record.message_id,
            value=record.model_dump(),
        )

        return {}

    return extract_data_after_agent_node
