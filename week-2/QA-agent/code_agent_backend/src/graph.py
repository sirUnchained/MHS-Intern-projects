from langchain_groq import ChatGroq
from langchain_ollama.embeddings import OllamaEmbeddings
from langgraph.graph import StateGraph, START, END
from langgraph.prebuilt import ToolNode
import psycopg
from psycopg.rows import dict_row
from langgraph.store.postgres import PostgresStore
from langgraph.checkpoint.postgres import PostgresSaver
from langchain_ollama.embeddings import OllamaEmbeddings
from psycopg_pool import ConnectionPool

from config import get_settings
from src.state import SupportState

from src.nodes.question_classifier import (
    get_question_classifier_node,
    question_classifier_route,
)
from src.nodes.building_classifier import get_building_classifier_and_ticket_node
from src.nodes.ticket import get_insert_ticket_node
from src.nodes.main_agent import get_main_agent_node, main_agent_route
from src.nodes.tool_limit import tool_limit_reached_node
from src.nodes.validator import (
    main_agent_response_validator_node,
    main_agent_validation_route,
)
from src.nodes.memory import get_extract_data_after_agent_node

from src.tools.retriever_tool import get_retriever_tool
from src.tools.search_tool import get_search_tool
from src.tools.financial_data_tool import get_financial_data_tool


def build_graph():
    settings = get_settings()

    # Setup LLMs and graph
    large_language_model = ChatGroq(
        model=settings.GROQ_MODEL_NAME, api_key=settings.GROQ_API_KEY, temperature=0.7
    )
    small_language_model = ChatGroq(
        model=settings.GROQ_CLASSIFY_MODEL_NAME,
        api_key=settings.GROQ_API_KEY,
        temperature=0.5,
    )
    embedding_model = OllamaEmbeddings(model=settings.OLLAMA_EMBEDDING_MODEL_NAME)

    graph_builder = StateGraph(SupportState)

    # Insert nodes
    graph_builder.add_node(
        "question_classifier_node", get_question_classifier_node(small_language_model)
    )
    graph_builder.add_node(
        "building_classifier_and_ticket_node",
        get_building_classifier_and_ticket_node(small_language_model),
    )
    graph_builder.add_node("insert_ticket_node", get_insert_ticket_node())
    graph_builder.add_node(
        "main_agent_node", get_main_agent_node(large_language_model, embedding_model)
    )
    graph_builder.add_node(
        "tools",
        ToolNode(
            [
                get_retriever_tool(embedding_model),
                get_financial_data_tool(),
                get_search_tool(),
            ]
        ),
    )
    graph_builder.add_node("tool_limit_reached_node", tool_limit_reached_node)
    graph_builder.add_node(
        "main_agent_response_validator_node", main_agent_response_validator_node
    )
    graph_builder.add_node(
        "extract_data_after_agent_node",
        get_extract_data_after_agent_node(small_language_model),
    )

    # Setup edges

    ## START --> question_classifier_node
    graph_builder.add_edge(START, "question_classifier_node")
    graph_builder.add_conditional_edges(
        "question_classifier_node",
        question_classifier_route,
        {
            "main_agent_node": "main_agent_node",
            "building_classifier_and_ticket_node": "building_classifier_and_ticket_node",
        },
    )

    ## building_classifier_and_ticket_node --> insert_ticket_node
    graph_builder.add_edge("building_classifier_and_ticket_node", "insert_ticket_node")

    ## insert_ticket_node --> END
    graph_builder.add_edge("insert_ticket_node", END)

    ## tools --> main_agent_node
    graph_builder.add_edge("tools", "main_agent_node")

    ## main_agent_node --> tools | main_agent_node --> main_agent_response_validator_node | tools --> tool_limit_reached_node
    graph_builder.add_conditional_edges(
        "main_agent_node",
        main_agent_route,
        {
            "tools": "tools",
            "tool_limit_reached_node": "tool_limit_reached_node",
            "main_agent_response_validator_node": "main_agent_response_validator_node",
        },
    )

    ## tool_limit_reached_node --> main_agent_node
    graph_builder.add_edge("tool_limit_reached_node", "main_agent_node")

    ## main_agent_response_validator_node --> extract_data_after_agent_node | main_agent_response_validator_node --> building_classifier_and_ticket_node
    graph_builder.add_conditional_edges(
        "main_agent_response_validator_node",
        main_agent_validation_route,
        {
            "extract_data_after_agent_node": "extract_data_after_agent_node",
            "building_classifier_and_ticket_node": "building_classifier_and_ticket_node",
        },
    )

    ## extract_data_after_agent_node --> END
    graph_builder.add_edge("extract_data_after_agent_node", END)

    # Build and return graph
    store, checkpointer = setup_memory()
    return graph_builder.compile(checkpointer=checkpointer, store=store)


def setup_memory():
    settings = get_settings()

    embedding_model = OllamaEmbeddings(model=settings.OLLAMA_EMBEDDING_MODEL_NAME)
    EMBED_DIMS = len(embedding_model.embed_query("dimension probe"))

    # --- Long-term memory ---
    store_conn = psycopg.connect(
        conninfo=settings.POSTGRESQL_DATABASE_LINK,
        autocommit=True,
        row_factory=dict_row,
    )
    store = PostgresStore(
        conn=store_conn,
        index={
            "embed": embedding_model,
            "dims": EMBED_DIMS,
        },
    )
    store.setup()

    # --- Shared connection pool ---
    pool = ConnectionPool(
        conninfo=settings.POSTGRESQL_DATABASE_LINK,
        kwargs={"autocommit": True, "row_factory": dict_row},
        max_size=20,
        open=True,
    )

    # --- Short-term memory ---
    checkpointer = PostgresSaver(conn=pool)
    checkpointer.setup()

    return (store, checkpointer)
