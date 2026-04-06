from gtts import gTTS
import os
import logging
from datetime import datetime

class TextToSpeech:

    def __init__(self, lang="hi"):
        """
        Initialize text to speech
        Args:
            lang: Language code (hi, en, ta, te, ml, kn, etc.)
        """
        self.lang = lang
        self.output_dir = "audio_output"
        os.makedirs(self.output_dir, exist_ok=True)
        logging.info(f"Text to speech initialized with language: {lang}")

    def generate_audio(self, text, filename=None):
        """Generate audio from text"""
        if not text:
            logging.warning("Empty text provided")
            return None
        
        try:
            # Create filename if not provided
            if not filename:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"speech_{timestamp}.mp3"
            
            file_path = os.path.join(self.output_dir, filename)
            
            # Generate speech
            tts = gTTS(text=text, lang=self.lang, slow=False)
            tts.save(file_path)
            
            logging.info(f"Audio saved: {file_path}")
            return file_path
            
        except Exception as e:
            logging.error(f"Text to speech failed: {e}")
            return None

    def generate_audio_with_rate(self, text, filename=None, slow=False):
        """Generate audio with speed control"""
        if not text:
            return None
        
        try:
            if not filename:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"speech_{timestamp}.mp3"
            
            file_path = os.path.join(self.output_dir, filename)
            
            tts = gTTS(text=text, lang=self.lang, slow=slow)
            tts.save(file_path)
            
            return file_path
            
        except Exception as e:
            logging.error(f"Failed: {e}")
            return None

    def cleanup_old_audio(self, days=7):
        """Delete audio files older than specified days"""
        import time
        current_time = time.time()
        
        for filename in os.listdir(self.output_dir):
            file_path = os.path.join(self.output_dir, filename)
            if os.path.isfile(file_path):
                file_age = current_time - os.path.getctime(file_path)
                if file_age > (days * 86400):  # days to seconds
                    os.remove(file_path)
                    logging.info(f"Removed old audio: {filename}")