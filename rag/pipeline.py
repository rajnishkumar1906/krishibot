from typing import List, Optional, Dict, Any
from langchain_core.documents import Document
import logging

class RAGPipeline:
    """Enhanced RAG pipeline with confidence scoring and streaming"""

    def __init__(self, retriever, generator):
        self.retriever = retriever
        self.generator = generator
        logging.info("RAG Pipeline initialized")

    def run(self, query: str, k: int = 3, include_confidence: bool = False) -> Dict[str, Any]:
        """Run RAG pipeline with optional confidence scoring"""
        
        if include_confidence:
            # Get documents with scores
            docs_with_scores = self.retriever.retrieve_with_scores(query, k=k)
            docs = [doc for doc, _ in docs_with_scores]
            scores = [score for _, score in docs_with_scores]
            avg_confidence = sum(scores) / len(scores) if scores else 0
        else:
            docs = self.retriever.retrieve(query, k=k)
            scores = None
            avg_confidence = None
        
        context = "\n\n".join([doc.page_content for doc in docs])
        answer = self.generator.generate(context, query)
        
        result = {
            "answer": answer,
            "retrieved_docs": docs,
            "num_docs": len(docs)
        }
        
        if include_confidence:
            result["confidence_scores"] = scores
            result["avg_confidence"] = avg_confidence
        
        logging.info(f"Generated answer for query: {query[:50]}...")
        return result
    
    def run_stream(self, query: str, k: int = 3):
        """Stream the response"""
        docs = self.retriever.retrieve(query, k=k)
        context = "\n\n".join([doc.page_content for doc in docs])
        
        for chunk in self.generator.generate_stream(context, query):
            yield chunk
    
    def run_with_sources(self, query: str, k: int = 3) -> Dict[str, Any]:
        """Get answer with source documents"""
        result = self.run(query, k=k)
        
        sources = []
        for doc in result["retrieved_docs"]:
            sources.append({
                "content": doc.page_content[:200] + "...",  # Preview
                "source": doc.metadata.get("source", "unknown"),
                "type": doc.metadata.get("type", "unknown")
            })
        
        result["sources"] = sources
        return result