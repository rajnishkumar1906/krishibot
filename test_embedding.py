from rag.embeddings import EmbeddingModel
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)

try:
    # Initialize the embedding model
    print("Initializing embedding model...")
    embedding_model = EmbeddingModel()
    
    # Test with a simple text
    test_text = "Hello, world!"
    print(f"Generating embedding for: '{test_text}'")
    
    result = embedding_model.model.embed_query(test_text)
    print(f"✅ Embedding generated successfully!")
    print(f"Vector dimension: {len(result)}")
    print(f"First 5 values: {result[:5]}")
    
    # Test with multiple texts
    texts = ["Hello", "World", "Testing embeddings"]
    print(f"\nTesting batch embedding with {len(texts)} texts...")
    
    results = embedding_model.model.embed_documents(texts)
    print(f"✅ Batch embedding generated successfully!")
    print(f"Number of embeddings: {len(results)}")
    print(f"Each vector dimension: {len(results[0])}")
    
except ValueError as e:
    print(f"❌ Configuration error: {e}")
    print("Make sure your krishibot.env file contains HUGGINGFACE_API_TOKEN")
except Exception as e:
    print(f"❌ Error: {e}")
    print(f"Error type: {type(e).__name__}")