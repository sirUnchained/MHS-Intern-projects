from langchain_core.documents import Document
from langchain_core.embeddings import Embeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_postgres import PGVector

from app.core.config import get_settings


def get_vector_store(embedding_model: Embeddings) -> PGVector:
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
    """Split text into chunks, embed them, and store in the vector DB.
    Returns the number of chunks stored."""
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
