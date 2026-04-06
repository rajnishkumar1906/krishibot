from rag.base import BaseRetriever
from typing import List, Optional
from langchain_core.documents import Document
import logging

class Retriever(BaseRetriever):
    """Enhanced retriever with multiple retrieval strategies"""

    def __init__(self, vector_store):
        self.vector_store = vector_store
        logging.info("Retriever initialized")

    def retrieve(self, query: str, k: int = 3) -> List[Document]:
        """Retrieve relevant documents"""
        return self.vector_store.search(query, k=k)
    
    def retrieve_with_scores(self, query: str, k: int = 3) -> List[tuple]:
        """Retrieve with similarity scores for confidence"""
        return self.vector_store.search_with_scores(query, k=k)
    
    def retrieve_filtered(self, query: str, k: int = 3, source_filter: Optional[str] = None) -> List[Document]:
        """Retrieve with source filtering"""
        docs = self.retrieve(query, k=k)
        
        if source_filter:
            docs = [doc for doc in docs if doc.metadata.get('source', '') == source_filter]
        
        return docs