from src.prompts import QUESTION_CLASSIFIER_SYSTEM_PROMPT
from src.state import SupportState
from typing import Literal


def get_question_classifier_node(llm):
    def question_classifier_node(state: SupportState) -> dict:
        """
        This is Router decistion node, in this node, llm must chose between 2 literals:
        * rag
        * escalate
        """

        question = state["messages"][-1]

        result = llm.invoke(
            [
                {"role": "system", "content": QUESTION_CLASSIFIER_SYSTEM_PROMPT},
                {"role": "user", "content": question.text},
            ]
        )

        route: Literal["rag", "escalate"] = (
            "rag" if "rag" in result.text.lower() else "escalate"
        )

        return {"route": route, "tool_calls_count": 0}

    return question_classifier_node


def question_classifier_route(state: SupportState):
    chosen_route = state["route"]

    if "rag" in chosen_route.lower():
        return "main_agent_node"
    else:
        return "building_classifier_and_ticket_node"
