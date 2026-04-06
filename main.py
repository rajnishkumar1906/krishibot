import os
import shutil
import tempfile
import logging
from typing import Optional
from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.responses import FileResponse, JSONResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
import uvicorn
from dotenv import load_dotenv

from modules import ingestion, retrieval, llm, speech

load_dotenv()
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI
app = FastAPI(
    title="KrishiBot - AI Agriculture Assistant",
    description="Voice-enabled RAG system for farmers",
    version="2.0.0",
    docs_url="/api/docs",
    redoc_url="/api/redoc"
)

# Security middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=os.getenv("ALLOWED_ORIGINS", "*").split(","),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.add_middleware(
    TrustedHostMiddleware,
    allowed_hosts=os.getenv("ALLOWED_HOSTS", "*").split(",")
)

# Ensure directories exist
os.makedirs("static", exist_ok=True)
os.makedirs("data", exist_ok=True)

# Mount static files
app.mount("/static", StaticFiles(directory="static"), name="static")

# ========== UI ROUTES ==========

@app.get("/", response_class=HTMLResponse)
async def serve_ui():
    """Serve the main UI page"""
    ui_path = "static/index.html"
    if os.path.exists(ui_path):
        with open(ui_path, 'r', encoding='utf-8') as f:
            return f.read()
    return HTMLResponse(content="""
    <!DOCTYPE html>
    <html>
    <head>
        <title>KrishiBot</title>
        <style>
            body {
                font-family: Arial, sans-serif;
                text-align: center;
                padding: 50px;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: white;
            }
            .container {
                max-width: 600px;
                margin: 0 auto;
                background: white;
                padding: 30px;
                border-radius: 15px;
                color: #333;
            }
            h1 { color: #2e7d32; }
            .status { color: #666; margin: 20px 0; }
            .btn {
                background: #2e7d32;
                color: white;
                padding: 12px 24px;
                border: none;
                border-radius: 8px;
                cursor: pointer;
                font-size: 16px;
                margin: 10px;
            }
            .btn:hover { background: #1b5e20; }
            .error { color: #d32f2f; }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>🚜 KrishiBot</h1>
            <p>Your AI Agriculture Assistant</p>
            <div class="status">
                <p>⚠️ UI file not found. Please create static/index.html</p>
                <p>API is running at:</p>
                <code>/api/chat/text</code> - Text chat<br>
                <code>/api/chat/voice</code> - Voice chat<br>
                <code>/api/health</code> - Health check<br>
                <code>/api/docs</code> - API documentation
            </div>
            <button class="btn" onclick="location.href='/api/docs'">View API Docs</button>
        </div>
    </body>
    </html>
    """, status_code=200)

@app.get("/api")
async def api_root():
    """API root endpoint"""
    return {
        "name": "KrishiBot API",
        "version": "2.0.0",
        "status": "running",
        "endpoints": {
            "ui": "/",
            "text_chat": "/api/chat/text",
            "voice_chat": "/api/chat/voice",
            "ingest": "/api/ingest",
            "health": "/api/health",
            "status": "/api/status",
            "docs": "/api/docs"
        }
    }

# ========== HEALTH & STATUS ==========

@app.get("/api/health")
async def health_check():
    """Health check endpoint"""
    vector_db_exists = os.path.exists("vector_db/faiss_index")
    data_files_count = len([f for f in os.listdir("data") if f.endswith(('.txt', '.pdf'))]) if os.path.exists("data") else 0
    
    return {
        "status": "healthy",
        "vector_db_loaded": vector_db_exists,
        "data_files": data_files_count,
        "services": {
            "llm": "google_gemini",
            "embeddings": "local_huggingface",
            "stt": "whisper",
            "tts": "edge_tts"
        },
        "api_key_configured": bool(os.getenv("GOOGLE_API_KEY"))
    }

@app.get("/api/status")
async def get_status():
    """Get detailed system status"""
    vector_db_exists = os.path.exists("vector_db/faiss_index")
    data_files = []
    
    if os.path.exists("data"):
        data_files = [f for f in os.listdir("data") if f.endswith(('.txt', '.pdf'))]
    
    return {
        "vector_db": vector_db_exists,
        "data_files": {
            "count": len(data_files),
            "files": data_files
        },
        "static_files": len(os.listdir("static")) if os.path.exists("static") else 0,
        "environment": {
            "google_api_key": "✅ configured" if os.getenv("GOOGLE_API_KEY") else "❌ missing",
            "huggingface_api_key": "✅ configured" if os.getenv("HUGGINGFACE_API_KEY") else "⚠️ optional"
        }
    }

# ========== KNOWLEDGE BASE MANAGEMENT ==========

@app.post("/api/ingest")
async def ingest_documents(force: bool = False):
    """Trigger document ingestion to rebuild knowledge base"""
    try:
        result = ingestion.run_ingestion(force=force)
        return {"message": result}
    except Exception as e:
        logger.error(f"Ingestion failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/rebuild")
async def rebuild_knowledge_base():
    """Alias for /api/ingest with force=True"""
    return await ingest_documents(force=True)

# ========== CHAT ENDPOINTS ==========

@app.post("/api/chat/text")
async def chat_text(
    query: str = Form(...),
    mode: str = Form("Hindi"),
    include_context: bool = Form(False)
):
    """Text chat endpoint - send text question, get text response"""
    try:
        # Validate input
        if not query or len(query.strip()) == 0:
            raise HTTPException(status_code=400, detail="Query cannot be empty")
        
        # Get context from knowledge base
        context = retrieval.get_context(query)
        
        # Generate response
        bot_text = llm.get_farmer_advice(query, context, mode)
        
        response = {
            "success": True,
            "query": query,
            "response": bot_text,
            "mode": mode
        }
        
        if include_context:
            response["context"] = context
        
        return response
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Chat error: {e}")
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")

@app.post("/api/chat/voice")
async def chat_voice(
    audio: UploadFile = File(...),
    mode: str = Form("Hindi")
):
    """Voice chat endpoint - send audio, get text + audio response"""
    temp_path = None
    
    try:
        # Validate audio file
        if not audio.filename:
            raise HTTPException(status_code=400, detail="No audio file provided")
        
        valid_extensions = ('.wav', '.mp3', '.m4a', '.webm')
        if not audio.filename.lower().endswith(valid_extensions):
            raise HTTPException(
                status_code=400, 
                detail=f"Invalid audio format. Use: {', '.join(valid_extensions)}"
            )
        
        # Save uploaded audio temporarily
        suffix = os.path.splitext(audio.filename)[1]
        with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as temp_file:
            shutil.copyfileobj(audio.file, temp_file)
            temp_path = temp_file.name
        
        logger.info(f"Audio saved: {temp_path}")
        
        # Speech to text
        user_text = speech.stt(temp_path)
        
        if not user_text or user_text.startswith("Error"):
            error_msg = user_text if user_text else "Could not understand audio"
            raise HTTPException(status_code=400, detail=error_msg)
        
        logger.info(f"Transcribed: {user_text}")
        
        # Get context and generate response
        context = retrieval.get_context(user_text)
        bot_text = llm.get_farmer_advice(user_text, context, mode)
        
        if not bot_text or bot_text.startswith("Error"):
            error_msg = bot_text if bot_text else "Could not generate response"
            raise HTTPException(status_code=500, detail=error_msg)
        
        logger.info(f"Generated response: {bot_text[:100]}...")
        
        # Generate speech response
        audio_path = await speech.tts(bot_text, mode)
        
        if not audio_path:
            logger.warning("TTS failed, returning text only")
            return {
                "success": True,
                "farmer_said": user_text,
                "bot_text": bot_text,
                "audio_url": None,
                "warning": "Audio generation failed"
            }
        
        return {
            "success": True,
            "farmer_said": user_text,
            "bot_text": bot_text,
            "audio_url": f"/static/{os.path.basename(audio_path)}"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Voice chat error: {e}")
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")
    
    finally:
        # Clean up temp file
        if temp_path and os.path.exists(temp_path):
            try:
                os.unlink(temp_path)
                logger.info(f"Cleaned up: {temp_path}")
            except Exception as e:
                logger.warning(f"Failed to delete temp file: {e}")

# ========== AUDIO SERVING ==========

@app.get("/api/audio/{filename}")
async def get_audio(filename: str):
    """Serve generated audio files"""
    # Security: prevent path traversal
    if ".." in filename or "/" in filename or "\\" in filename:
        raise HTTPException(status_code=400, detail="Invalid filename")
    
    file_path = f"static/{filename}"
    if os.path.exists(file_path) and os.path.isfile(file_path):
        return FileResponse(
            file_path, 
            media_type="audio/mpeg",
            headers={
                "Cache-Control": "public, max-age=3600",
                "Content-Disposition": "inline"
            }
        )
    raise HTTPException(status_code=404, detail="Audio file not found")

# ========== FALLBACK FOR OLD ENDPOINTS ==========

@app.post("/chat")
async def chat_legacy(
    audio: UploadFile = File(...),
    mode: str = Form("Hindi")
):
    """Legacy endpoint for backward compatibility"""
    return await chat_voice(audio, mode)

# ========== STARTUP EVENT ==========

@app.on_event("startup")
async def startup_event():
    """Run on application startup"""
    logger.info("=" * 50)
    logger.info("🚀 KrishiBot Starting Up...")
    logger.info("=" * 50)
    
    # Check API keys
    if not os.getenv("GOOGLE_API_KEY"):
        logger.warning("⚠️ GOOGLE_API_KEY not set! Text generation will not work.")
    else:
        logger.info("✅ Google Gemini API key configured")
    
    if os.getenv("HUGGINGFACE_API_KEY"):
        logger.info("✅ Hugging Face API key configured (for cloud embeddings if needed)")
    
    # Check vector database
    if os.path.exists("vector_db/faiss_index"):
        logger.info("✅ Vector database found and ready")
    else:
        logger.warning("⚠️ Vector database not found! Run ingestion first:")
        logger.warning("   python -c 'from modules.ingestion import run_ingestion; print(run_ingestion(force=True))'")
    
    # Check data folder
    if os.path.exists("data"):
        files = [f for f in os.listdir("data") if f.endswith(('.txt', '.pdf'))]
        if files:
            logger.info(f"📚 Found {len(files)} knowledge files in /data folder")
            for f in files:
                logger.info(f"   - {f}")
        else:
            logger.warning("⚠️ No .txt or .pdf files found in /data folder")
    
    logger.info("=" * 50)
    logger.info("🌐 KrishiBot is ready!")
    logger.info("📱 UI: http://127.0.0.1:8000")
    logger.info("📚 API Docs: http://127.0.0.1:8000/api/docs")
    logger.info("=" * 50)

# ========== MAIN ENTRY POINT ==========

if __name__ == "__main__":
    port = int(os.getenv("PORT", 8000))
    host = os.getenv("HOST", "0.0.0.0")
    
    uvicorn.run(
        app,
        host=host,
        port=port,
        log_level="info",
        reload=True  # Enable auto-reload for development
    )