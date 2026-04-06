from transformers import pipeline
import logging
import os

class SpeechToText:

    def __init__(self, model_name="openai/whisper-base", language=None):
        """
        Initialize speech to text model
        Args:
            model_name: Whisper model size (tiny, base, small, medium, large)
            language: Language code (e.g., "hi" for Hindi, "ta" for Tamil)
        """
        self.model_name = model_name
        self.language = language
        try:
            self.pipe = pipeline(
                "automatic-speech-recognition",
                model=model_name
            )
            logging.info(f"Speech to text model loaded: {model_name}")
        except Exception as e:
            logging.error(f"Failed to load speech model: {e}")
            raise

    def transcribe(self, file_path):
        """Transcribe audio file to text"""
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"Audio file not found: {file_path}")
        
        try:
            # Set generation parameters
            generate_kwargs = {}
            if self.language:
                generate_kwargs["language"] = self.language
            
            result = self.pipe(file_path, generate_kwargs=generate_kwargs)
            
            text = result["text"]
            logging.info(f"Transcribed: {text[:50]}...")
            return text
            
        except Exception as e:
            logging.error(f"Transcription failed: {e}")
            return ""

    def transcribe_batch(self, file_paths):
        """Transcribe multiple audio files"""
        results = []
        for file_path in file_paths:
            text = self.transcribe(file_path)
            results.append({"file": file_path, "text": text})
        return results