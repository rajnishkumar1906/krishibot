import os
import logging
from utils.config import Config

# Set HuggingFace token to avoid warnings and speed up loading
os.environ["HF_TOKEN"] = Config.HUGGINGFACE_API_TOKEN
os.environ["TOKENIZERS_PARALLELISM"] = "false"

from rag.embeddings import EmbeddingModel
from rag.vector_store import FAISSVectorStore
from rag.retriever import Retriever
from rag.generator import GeminiGenerator
from rag.pipeline import RAGPipeline

class AppContainer:
    """Application dependency container"""

    def __init__(self):
        self.embedding = None
        self.vector_store = None
        self.retriever = None
        self.generator = None
        self.pipeline = None
        
        self._initialize()
    
    def _initialize(self):
        """Initialize all components with error handling"""
        try:
            # Check if vector store exists
            if not os.path.exists("vector_store/faiss_index"):
                raise FileNotFoundError(
                    "Vector store not found. Please run ingest.py first."
                )
            
            # Initialize embedding model
            logging.info("Initializing embedding model...")
            self.embedding = EmbeddingModel()
            
            # Load vector store
            logging.info("Loading vector store...")
            self.vector_store = FAISSVectorStore()
            self.vector_store.load("vector_store/faiss_index", self.embedding)
            
            # Initialize retriever
            logging.info("Initializing retriever...")
            self.retriever = Retriever(self.vector_store)
            
            # Initialize generator
            logging.info("Initializing Gemini generator...")
            if not Config.GEMINI_API_KEY:
                raise ValueError("GEMINI_API_KEY not found in environment variables")
            self.generator = GeminiGenerator(Config.GEMINI_API_KEY,embedding_model=self.embedding)
            
            # Initialize pipeline
            logging.info("Initializing RAG pipeline...")
            self.pipeline = RAGPipeline(self.retriever, self.generator)
            
            logging.info("App container initialized successfully")
            
        except Exception as e:
            logging.error(f"Failed to initialize app container: {e}")
            raise

    def reload_vector_store(self):
        """Reload vector store (useful after updating knowledge base)"""
        if self.embedding:
            self.vector_store.load("vector_store/faiss_index", self.embedding)
            logging.info("Vector store reloaded")
            return True
        return False

# Create singleton instance
container = AppContainer()
rag_pipeline = container.pipeline