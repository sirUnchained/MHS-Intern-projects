from langchain_core.documents import Document
from langchain_core.embeddings import Embeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_postgres import PGVector

from app.core.config import get_settings


def get_vector_store(embedding_model: Embeddings) -> PGVector:
    """
    Create or retrieve a PostgreSQL vector store instance for RAG operations.

    This function initializes a PGVector connection using the application's
    database settings and a fixed collection name. The collection name is
    intentionally synchronized with the retriever tool's collection (defined
    in src/rag/vector_store.py), ensuring that any documents ingested via
    this store are immediately available for retrieval queries.

    Args:
        embedding_model (Embeddings): The embedding model instance used to
            convert text into vector representations. This must be compatible
            with the PGVector's expected embedding format.

    Returns:
        PGVector: A configured PGVector instance connected to the PostgreSQL
            database with the collection "RAG_documents_vectores". The returned
            object supports document addition and similarity search operations.

    Notes:
        - The collection name must remain consistent across all RAG components
          to maintain a unified vector index.
        - Connection details are sourced from application settings via
          get_settings().
        - This function does not create the collection if it doesn't exist;
          PGVector handles this automatically on first use.
    """

    settings = get_settings()
    # Same collection name used by src/rag/vector_store.py's retriever,
    # so anything ingested here is immediately searchable by retriever_tool.
    return PGVector(
        embeddings=embedding_model,
        connection=settings.POSTGRESQL_DATABASE_LINK,
        collection_name="RAG_documents_vectores",
    )


def ingest_text(
    text: str,
    source_name: str,
    embedding_model: Embeddings,
    chunk_size: int = 1000,
    chunk_overlap: int = 150,
) -> int:
    """
    Ingest text into the vector database for RAG retrieval.

    This function processes raw text by splitting it into manageable chunks,
    generating embeddings for each chunk, and storing them in the PostgreSQL
    vector store. Each chunk is associated with its source and index position
    for traceability and potential debugging.

    Args:
        text (str): The raw text content to be ingested and indexed for
            retrieval. Must be non-empty.
        source_name (str): Identifier for the text's origin (e.g., filename,
            URL, or document ID). This is stored as metadata for each chunk
            to enable source attribution in retrieval results.
        embedding_model (Embeddings): The embedding model used to convert
            text chunks into vector representations. Must match the model
            used by the retriever for consistent search results.
        chunk_size (int, optional): Maximum number of characters per chunk.
            Defaults to 1000. Smaller chunks improve retrieval precision but
            increase storage and processing overhead.
        chunk_overlap (int, optional): Number of characters to overlap between
            consecutive chunks. Defaults to 150. Helps maintain context across
            chunk boundaries and prevents information loss at split points.

    Returns:
        int: The number of document chunks successfully stored in the vector
            database. Returns 0 if the input text is empty or whitespace-only.
    """

    if not text.strip():
        return 0

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size, chunk_overlap=chunk_overlap
    )
    chunks = splitter.split_text(text)

    docs = [
        Document(page_content=chunk, metadata={"source": source_name, "chunk_index": i})
        for i, chunk in enumerate(chunks)
    ]

    vector_store = get_vector_store(embedding_model)
    vector_store.add_documents(docs)
    return len(docs)
