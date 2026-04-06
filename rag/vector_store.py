from langchain_community.vectorstores import FAISS
from rag.base import BaseVectorStore
from typing import List, Optional
from langchain_core.documents import Document
import logging
import os

class FAISSVectorStore(BaseVectorStore):
    """Enhanced FAISS vector store for agricultural documents"""

    def __init__(self):
        self.db = None
        self.embedding_model = None
        logging.info("FAISS vector store initialized")

    def create(self, docs: List[Document], embedding) -> None:
        """Create vector store from documents"""
        if not docs:
            logging.warning("No documents provided for vector store creation")
            return
        
        self.embedding_model = embedding
        self.db = FAISS.from_documents(docs, embedding.model)
        logging.info(f"Created vector store with {len(docs)} documents")

    def save(self, path: str) -> None:
        """Save vector store to disk"""
        if self.db:
            os.makedirs(os.path.dirname(path), exist_ok=True)
            self.db.save_local(path)
            logging.info(f"Vector store saved to {path}")
        else:
            logging.error("No vector store to save")

    def load(self, path: str, embedding) -> None:
        """Load vector store from disk"""
        self.embedding_model = embedding
        self.db = FAISS.load_local(
            path,
            embedding.model,
            allow_dangerous_deserialization=True
        )
        logging.info(f"Vector store loaded from {path}")

    def search(self, query: str, k: int = 3) -> List[Document]:
        """Search for similar documents"""
        if not self.db:
            logging.error("Vector store not initialized")
            return []
        
        results = self.db.similarity_search(query, k=k)
        logging.info(f"Retrieved {len(results)} documents for query: {query[:50]}...")
        return results
    
    def search_with_scores(self, query: str, k: int = 3) -> List[tuple]:
        """Search with similarity scores"""
        if not self.db:
            logging.error("Vector store not initialized")
            return []
        
        results = self.db.similarity_search_with_score(query, k=k)
        logging.info(f"Retrieved {len(results)} documents with scores")
        return results
    
    def add_documents(self, docs: List[Document]) -> None:
        """Add documents to existing vector store"""
        if not self.db:
            logging.error("Vector store not initialized. Create or load first.")
            return
        
        self.db.add_documents(docs)
        logging.info(f"Added {len(docs)} documents to vector store")
    
    def delete(self, ids: Optional[List[str]] = None) -> None:
        """Delete documents (requires FAISS index manipulation)"""
        # FAISS doesn't support direct deletion, so we log a warning
        logging.warning("FAISS doesn't support direct deletion. Consider recreating the index.")