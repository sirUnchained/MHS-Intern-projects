from langchain_core.embeddings import Embeddings
from langchain_postgres import PGVector
from app.core.config import get_settings


def get_retriever(embedding_model: Embeddings, k: int = 3):
    """
    Create a retriever instance for RAG (Retrieval-Augmented Generation) queries.

    This function initializes a PGVector-backed retriever connected to the
    application's vector store collection.

    Args:
        embedding_model (Embeddings): The embedding model used to convert
            query text into vector representations for similarity comparison.
            Must be the same model that was used during document ingestion
            to ensure consistent vector space alignment.
        k (int, optional): The number of most relevant document chunks to
            retrieve per query. Defaults to 3. Higher values provide more
            context but may introduce noise and increase token usage in
            downstream LLM calls. Lower values improve speed but may miss
            relevant information.

    Returns:
        PGVectorRetriever: A configured retriever object with the following
    """

    settings = get_settings()

    vector_store = PGVector(
        embeddings=embedding_model,
        connection=settings.POSTGRESQL_DATABASE_LINK,
        collection_name="RAG_documents_vectores",
    )

    return vector_store.as_retriever(search_kwargs={"k": k})
