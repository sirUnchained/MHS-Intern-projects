from langchain_groq import ChatGroq
from langchain_google_genai.embeddings import GoogleGenerativeAIEmbeddings
from langgraph.graph import StateGraph, START, END
from langgraph.prebuilt import ToolNode
from psycopg.rows import dict_row

from langgraph.store.postgres.aio import AsyncPostgresStore
from langgraph.checkpoint.postgres.aio import AsyncPostgresSaver
from psycopg_pool import AsyncConnectionPool

from app.core.config import get_settings
from agent.state import SupportState

from agent.nodes.question_classifier import (
    get_question_classifier_node,
    question_classifier_route,
)
from agent.nodes.building_classifier import get_building_classifier_and_ticket_node
from agent.nodes.ticket import get_insert_ticket_node
from agent.nodes.main_agent import get_main_agent_node, main_agent_route
from agent.nodes.tool_limit import tool_limit_reached_node
from agent.nodes.validator import (
    main_agent_response_validator_node,
    main_agent_validation_route,
)
from agent.nodes.memory import get_extract_data_after_agent_node

from agent.tools.retriever_tool import get_retriever_tool
from agent.tools.search_tool import get_search_tool
from agent.tools.financial_data_tool import get_financial_data_tool


async def build_graph():
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
    embedding_model = GoogleGenerativeAIEmbeddings(
        model=settings.GOOGLE_EMBEDDING_MODEL_NAME,
        api_key=settings.GOOGLE_API_KEY,
        output_dimensionality=1536,
    )

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
    store, checkpointer = await setup_memory(embedding_model=embedding_model)
    return graph_builder.compile(checkpointer=checkpointer, store=store)


async def setup_memory(embedding_model):
    settings = get_settings()

    EMBED_DIMS = len(await embedding_model.aembed_query("dimension probe"))

    # --- Shared async connection pool (used by both store and checkpointer) ---
    pool = AsyncConnectionPool(
        conninfo=settings.POSTGRESQL_DATABASE_LINK,
        kwargs={"autocommit": True, "row_factory": dict_row},
        max_size=5,
        open=False,
    )
    await pool.open()

    # --- Long-term memory ---
    store = AsyncPostgresStore(
        pool,
        index={
            "embed": embedding_model,
            "dims": EMBED_DIMS,
        },
    )
    await store.setup()

    # --- Short-term memory ---
    checkpointer = AsyncPostgresSaver(pool)
    await checkpointer.setup()

    return (store, checkpointer)
