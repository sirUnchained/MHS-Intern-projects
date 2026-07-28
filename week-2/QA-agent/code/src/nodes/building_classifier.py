from pydantic import BaseModel, Field
from src.helpers import safe_structured_invoke
from src.state import SupportState, UserTicketData
from src.prompts import DEPARTMENT_CLASSIFIER_TOKEN_SYSTEM_PROMPT
from langchain_core.messages import AIMessage
from config import SUPPORT_BUILDINGS


class UserTicketInfoStructure(BaseModel):
    building: str = Field(description="The building name which you detect.")
    topic: str = Field(description="Write a topic from user's input.")
    budget: str = Field(
        description='The user\'s stated budget or financial range (e.g., "$10,000-$20,000", "under $5,000", "unlimited")'
    )
    job: str = Field(
        description='The user\'s current occupation, profession, or role (e.g., "software engineer","retired teacher", "small business owner")'
    )
    goals: str = Field(
        description='The user\'s stated objectives or desired outcomes (e.g., "save for retirement", "buy a house", "start a business")'
    )


def format_buildings_for_prompt() -> str:
    lines = []
    for b in SUPPORT_BUILDINGS:
        lines.append(f"- {b['name']}: handles {', '.join(b['services'])}")
    return "\n".join(lines)


# building_classifier_and_ticket_node
def get_building_classifier_and_ticket_node(llm):
    def building_classifier_and_ticket_node(state: SupportState) -> dict:
        question = state["messages"][-1]

        result = safe_structured_invoke(
            llm.with_structured_output(UserTicketInfoStructure),
            [
                {
                    "role": "system",
                    "content": DEPARTMENT_CLASSIFIER_TOKEN_SYSTEM_PROMPT.format(
                        DEPARTMENTS=format_buildings_for_prompt()
                    ),
                },
                {"role": "user", "content": question.text},
            ],
            fallback=UserTicketInfoStructure(
                building="support",
                topic="",
                budget="",
                job="",
                goals="",
            ),
        )

        new_ticket = UserTicketData()
        for b in SUPPORT_BUILDINGS:
            # search if the LLM chosen name exists in our building list
            if result.building.lower() in b["name"].lower():
                new_ticket["topic"] = result.topic
                new_ticket["budget"] = result.budget
                new_ticket["job"] = result.job
                new_ticket["goals"] = result.goals
                new_ticket["building"] = b["name"]
                new_ticket["phone"] = b["phone"]
                new_ticket["services"] = b["services"]
                break

        return {
            "new_ticket": new_ticket,
            "messages": [
                AIMessage(
                    content=f"Agent response failed the validation, redirecting you'r request to {new_ticket['building']}"
                )
            ],
        }

    return building_classifier_and_ticket_node
