import os
import sys
import logging

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from rag.data_loader import DataLoader
from rag.chunker import Chunker
from rag.embeddings import EmbeddingModel
from rag.vector_store import FAISSVectorStore

# Setup logging with ASCII-only output to avoid Unicode errors
class AsciiLogger:
    """Filter out Unicode emojis for Windows console"""
    def __init__(self, logger):
        self.logger = logger
    
    def info(self, msg):
        # Replace emojis with ASCII equivalents or remove them
        msg = msg.replace('✅', '[OK]')
        msg = msg.replace('❌', '[ERROR]')
        msg = msg.replace('📚', '[DOCS]')
        msg = msg.replace('✂️', '[SPLIT]')
        msg = msg.replace('🧠', '[AI]')
        msg = msg.replace('🗄️', '[DB]')
        msg = msg.replace('💾', '[SAVE]')
        msg = msg.replace('🎉', '[SUCCESS]')
        msg = msg.replace('📊', '[STATS]')
        msg = msg.replace('🔍', '[TEST]')
        msg = msg.replace('=', '=')
        self.logger.info(msg)
    
    def error(self, msg):
        self.logger.error(msg)

# Setup basic logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = AsciiLogger(logging.getLogger(__name__))

try:
    # Load documents
    logger.info("Loading documents from data/raw...")
    loader = DataLoader()
    docs = loader.load_all("data/raw")
    logger.info(f"Loaded {len(docs)} documents")

    # Split into chunks
    logger.info("Splitting documents into chunks...")
    chunker = Chunker()
    chunks = chunker.split(docs)
    logger.info(f"Created {len(chunks)} chunks")

    # Create embeddings and vector store
    logger.info("Creating vector store...")
    embedding = EmbeddingModel()
    vector_store = FAISSVectorStore()
    vector_store.create(chunks, embedding)

    # Save vector store
    logger.info("Saving vector store...")
    os.makedirs("vector_store", exist_ok=True)
    vector_store.save("vector_store/faiss_index")

    print(f"\n[SUCCESS] Knowledge Base Created Successfully!")
    print(f"   Documents processed: {len(docs)}")
    print(f"   Chunks created: {len(chunks)}")
    print(f"   Location: vector_store/faiss_index")
    
    # Test retrieval
    print(f"\n[TEST] Testing retrieval...")
    test_query = "कृषि"
    test_results = vector_store.search(test_query, k=2)
    print(f"[OK] Test retrieval successful! Found {len(test_results)} results")
    print(f"\n[READY] You can now run the API server!")

except Exception as e:
    logger.error(f"Failed to create knowledge base: {e}")
    print(f"\n[ERROR] {e}")