import os
from typing import List, Optional
from langchain_community.document_loaders import TextLoader, CSVLoader, PyPDFLoader
from langchain_core.documents import Document
import logging

class DataLoader:
    """Load various agricultural document formats"""

    def __init__(self):
        self.supported_extensions = ['.txt', '.csv', '.pdf']
        logging.info("DataLoader initialized")

    def load_txt(self, path: str) -> List[Document]:
        """Load text file with encoding handling"""
        try:
            # Try UTF-8 first, fallback to other encodings
            try:
                loader = TextLoader(path, encoding="utf-8")
            except UnicodeDecodeError:
                loader = TextLoader(path, encoding="latin-1")
            
            docs = loader.load()
            
            # Add metadata
            for doc in docs:
                doc.metadata.update({
                    'source': os.path.basename(path),
                    'type': 'text',
                    'format': 'txt'
                })
            
            return docs
        except Exception as e:
            logging.error(f"Error loading {path}: {e}")
            return []

    def load_csv(self, path: str) -> List[Document]:
        """Load CSV file for agricultural data"""
        try:
            loader = CSVLoader(
                path,
                encoding="utf-8",
                csv_args={'delimiter': ','}
            )
            docs = loader.load()
            
            for doc in docs:
                doc.metadata.update({
                    'source': os.path.basename(path),
                    'type': 'tabular',
                    'format': 'csv'
                })
            
            return docs
        except Exception as e:
            logging.error(f"Error loading CSV {path}: {e}")
            return []

    def load_pdf(self, path: str) -> List[Document]:
        """Load PDF file for agricultural documents"""
        try:
            loader = PyPDFLoader(path)
            docs = loader.load()
            
            for doc in docs:
                doc.metadata.update({
                    'source': os.path.basename(path),
                    'type': 'document',
                    'format': 'pdf'
                })
            
            return docs
        except Exception as e:
            logging.error(f"Error loading PDF {path}: {e}")
            return []

    def load_all(self, folder: str, extension: Optional[str] = None) -> List[Document]:
        """Load all documents from folder"""
        docs = []
        
        if not os.path.exists(folder):
            logging.error(f"Folder not found: {folder}")
            return []
        
        for file in os.listdir(folder):
            file_path = os.path.join(folder, file)
            
            # Filter by extension if specified
            if extension and not file.endswith(extension):
                continue
            
            if file.endswith(".txt"):
                docs.extend(self.load_txt(file_path))
            elif file.endswith(".csv"):
                docs.extend(self.load_csv(file_path))
            elif file.endswith(".pdf"):
                docs.extend(self.load_pdf(file_path))
        
        logging.info(f"Loaded {len(docs)} documents from {folder}")
        return docs