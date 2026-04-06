from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional
from langchain_core.documents import Document

class BaseRetriever(ABC):
    @abstractmethod
    def retrieve(self, query: str, k: int = 3) -> List[Document]:
        """Retrieve relevant documents for a query"""
        pass
    
    @abstractmethod
    def retrieve_with_scores(self, query: str, k: int = 3) -> List[tuple]:
        """Retrieve documents with similarity scores"""
        pass


class BaseGenerator(ABC):
    @abstractmethod
    def generate(self, context: str, query: str, **kwargs) -> str:
        """Generate response based on context and query"""
        pass
    
    @abstractmethod
    def generate_stream(self, context: str, query: str):
        """Stream generated response"""
        pass


class BaseVectorStore(ABC):
    @abstractmethod
    def search(self, query: str, k: int = 3) -> List[Document]:
        """Search for similar documents"""
        pass
    
    @abstractmethod
    def search_with_scores(self, query: str, k: int = 3) -> List[tuple]:
        """Search with similarity scores"""
        pass
    
    @abstractmethod
    def add_documents(self, docs: List[Document]) -> None:
        """Add documents to vector store"""
        pass
    
    @abstractmethod
    def delete(self, ids: Optional[List[str]] = None) -> None:
        """Delete documents from vector store"""
        pass