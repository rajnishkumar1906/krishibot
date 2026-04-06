from langchain_text_splitters import RecursiveCharacterTextSplitter
from typing import List, Optional
from langchain_core.documents import Document
import logging

class Chunker:
    """Enhanced chunker optimized for agricultural content"""

    def __init__(self, chunk_size: int = 500, chunk_overlap: int = 50):
        self.splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            separators=["\n\n", "\n", ". ", " ", ""],
            keep_separator=False,
            add_start_index=True,  # Track original position
        )
        logging.info(f"Chunker initialized: size={chunk_size}, overlap={chunk_overlap}")

    def split(self, docs: List[Document]) -> List[Document]:
        """Split documents with metadata preservation"""
        if not docs:
            logging.warning("No documents to split")
            return []
        
        chunks = self.splitter.split_documents(docs)
        
        # Add agricultural metadata to chunks
        for chunk in chunks:
            if 'source' not in chunk.metadata:
                chunk.metadata['source'] = 'unknown'
            chunk.metadata['chunk_type'] = 'agricultural_content'
            
        logging.info(f"Split {len(docs)} docs into {len(chunks)} chunks")
        return chunks