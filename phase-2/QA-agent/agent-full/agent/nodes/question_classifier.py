from agent.prompts import QUESTION_CLASSIFIER_SYSTEM_PROMPT
from agent.state import SupportState
from typing import Literal


def get_question_classifier_node(llm):
    def question_classifier_node(state: SupportState) -> dict:
        """
        Route user queries by classifying them into one of two paths.

        Uses an LLM to determine if a question should be answered via RAG
        retrieval or escalated to a human agent.

        Args:
            state (SupportState): Conversation state containing the message history.
                The last message is classified.

        Returns:
            dict: State update containing the classification result. Expected
                values are "rag" or "escalate".

        Note:
            Uses QUESTION_CLASSIFIER_SYSTEM_PROMPT to guide the LLM's routing decision.
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
