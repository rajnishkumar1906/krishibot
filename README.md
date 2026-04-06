# KrishiBot 🌾

KrishiBot is a voice-enabled RAG (Retrieval-Augmented Generation) system designed to assist farmers with agricultural queries. It uses advanced AI models to provide accurate information about crop cultivation, agricultural laws, government schemes, and more, with support for voice interaction.

## Features 🚀

- **Voice Interaction**: Speech-to-Text (STT) and Text-to-Speech (TTS) capabilities for hands-free assistance.
- **RAG Pipeline**: Enhanced Retrieval-Augmented Generation using LangChain and Gemini API.
- **Agricultural Knowledge Base**: Pre-loaded with data on Indian agricultural laws, crop guides, pest control, and more.
- **Web Interface**: User-friendly frontend for easy interaction.
- **Multilingual Support**: Support for Hindi and other regional languages.

## Project Structure 📁

- `app/`: FastAPI application and API routes.
- `rag/`: RAG pipeline implementation, including document chunking, embeddings, and retrieval.
- `voice/`: Voice services for STT and TTS.
- `data/raw/`: Raw agricultural data files.
- `frontend/`: Web interface files (HTML, CSS, JS).
- `scripts/`: Data ingestion and processing scripts.
- `utils/`: Configuration and utility functions.

## Setup Instructions 🛠️

### Prerequisites
- Python 3.11+
- Gemini API Key
- HuggingFace API Token (for embeddings)

### Environment Setup

1. **Create a virtual environment**:
   ```bash
   python -m venv krishibotenv
   ```

2. **Activate the virtual environment**:
   - Windows:
     ```powershell
     .\krishibotenv\Scripts\activate
     ```
   - Linux/macOS:
     ```bash
     source krishibotenv/bin/activate
     ```

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure environment variables**:
   Create a `krishibot.env` file in the root directory and add your API keys:
   ```env
   GEMINI_API_KEY=your_gemini_api_key
   HUGGINGFACE_API_TOKEN=your_huggingface_token
   MODEL_NAME=gemini-1.5-pro
   ```

### Running the Application

1. **Ingest Data** (First time only):
   ```bash
   python scripts/ingest.py
   ```

2. **Start the Server**:
   ```bash
   python run.py
   ```
   The application will be available at `http://localhost:8000`.

## Technologies Used 💻

- **Framework**: FastAPI
- **LLM**: Google Gemini
- **Embeddings**: HuggingFace (sentence-transformers)
- **Vector Store**: FAISS
- **Orchestration**: LangChain
- **Voice**: gTTS, SpeechRecognition
- **Frontend**: HTML/CSS/JavaScript
