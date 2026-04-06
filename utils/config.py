import os
from dotenv import load_dotenv

load_dotenv("krishibot.env")

class Config:
    GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
    HUGGINGFACE_API_TOKEN = os.getenv("HUGGINGFACE_API_TOKEN")
    MODEL_NAME = os.getenv("MODEL_NAME")