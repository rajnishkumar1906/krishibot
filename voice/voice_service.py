from voice.speech_to_text import SpeechToText
from voice.text_to_speech import TextToSpeech
import logging
import os

class VoiceService:

    def __init__(self, stt_model="openai/whisper-base", tts_lang="hi"):
        """
        Initialize voice service for KrishiBot
        Args:
            stt_model: Whisper model for speech recognition
            tts_lang: Language for text-to-speech (hi, en, ta, etc.)
        """
        self.stt = SpeechToText(model_name=stt_model, language=tts_lang)
        self.tts = TextToSpeech(lang=tts_lang)
        logging.info("Voice service initialized")

    def process_audio(self, file_path):
        """Convert speech to text"""
        if not os.path.exists(file_path):
            logging.error(f"Audio file not found: {file_path}")
            return None
        
        try:
            text = self.stt.transcribe(file_path)
            return text
        except Exception as e:
            logging.error(f"Audio processing failed: {e}")
            return None

    def generate_audio(self, text, filename=None):
        """Convert text to speech"""
        if not text:
            logging.warning("No text to convert to speech")
            return None
        
        try:
            audio_file = self.tts.generate_audio(text, filename)
            return audio_file
        except Exception as e:
            logging.error(f"Audio generation failed: {e}")
            return None

    def process_and_respond(self, audio_file_path, response_text=None):
        """
        Complete voice interaction: listen -> process -> respond
        """
        # Step 1: Convert speech to text
        user_query = self.process_audio(audio_file_path)
        
        if not user_query:
            return None, None
        
        # Step 2: If response provided, convert to speech
        if response_text:
            audio_response = self.generate_audio(response_text)
            return user_query, audio_response
        
        return user_query, None

    def set_language(self, lang_code):
        """Change TTS language"""
        self.tts.lang = lang_code
        logging.info(f"TTS language changed to: {lang_code}")

    def get_supported_languages(self):
        """Get list of supported Indian languages"""
        return {
            "hi": "Hindi",
            "en": "English",
            "ta": "Tamil",
            "te": "Telugu",
            "ml": "Malayalam",
            "kn": "Kannada",
            "mr": "Marathi",
            "bn": "Bengali",
            "gu": "Gujarati",
            "pa": "Punjabi"
        }