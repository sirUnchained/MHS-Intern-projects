from langchain.tools import tool
from langchain_core.documents import Document
from typing import List
from src.rag.vector_store import get_retriever


def get_retriever_tool(embedding_model):

    @tool
    def retriever_tool(query: str) -> List[Document]:
        """
        Retrieve relevant documents from the vector database based on a semantic search query.

        This tool uses a pre-configured vector store retriever to find documents that are
        semantically similar to the input query. It's useful for fetching contextual
        information, historical data, or relevant knowledge from the stored document corpus.

        Args:
            query (str): The search query string. Should be a clear, descriptive question
                        or statement about the information you're looking for.

        Returns:
            List[Document]: A list of Document objects containing the most relevant
                            text chunks and their metadata, ordered by relevance.
        """
        vec_store_retriever = get_retriever(embedding_model=embedding_model)
        return vec_store_retriever.invoke(query)

    return retriever_tool
