from langchain_core.embeddings import Embeddings
from langchain_postgres import PGVector
from app.core.config import get_settings


def get_retriever(embedding_model: Embeddings, k: int = 3):
    settings = get_settings()

    vector_store = PGVector(
        embeddings=embedding_model,
        connection=settings.POSTGRESQL_DATABASE_LINK,
        collection_name="RAG_documents_vectores",
    )

    return vector_store.as_retriever(search_kwargs={"k": k})
