from langchain_huggingface import HuggingFaceEndpointEmbeddings
from utils.config import Config
import logging

class EmbeddingModel:

    def __init__(self):
        if not Config.HUGGINGFACE_API_TOKEN:
            raise ValueError("HUGGINGFACE_API_TOKEN not found in environment variables")
        
        try:
            self.model = HuggingFaceEndpointEmbeddings(
                model="sentence-transformers/all-MiniLM-L6-v2",
                huggingfacehub_api_token=Config.HUGGINGFACE_API_TOKEN,
                # Optional: Add timeout and task parameters
                # timeout=30,
                # task="feature-extraction"
            )
            logging.info("HuggingFace embedding model initialized successfully")
        except Exception as e:
            logging.error(f"Failed to initialize embedding model: {e}")
            raise