from google import genai
import logging
import re
import traceback
from utils.config import Config

class GeminiGenerator:
    def __init__(self, api_key: str, embedding_model=None):
        self.client = genai.Client(api_key=api_key)
        self.classifier = None
        if embedding_model:
            try:
                from rag.classifier import QueryClassifier
                self.classifier = QueryClassifier(embedding_model)
                logging.info("Query classifier initialized successfully.")
            except Exception as e:
                logging.error(f"Failed to initialize classifier: {e}")
                logging.error(traceback.format_exc())
        else:
            logging.warning("No embedding model – classifier disabled.")

        self.system_block = """
You are KrishiBot, for Indian farmers.
Mission: Increase yield, manage pests/diseases, weather impacts, govt schemes.

FORMATTING:
- NO markdown. No *, #, `, etc.
- Lists: 1. 2. 3. or A. B. C.
- Plain text only. Use CAPS sparingly for emphasis.

LANGUAGE & TONE:
- Respond in farmer's language (Hinglish/Hindi/English).
- Use "Aap", "Kisan bhai". Be respectful and encouraging.
- Short sentences. Avoid jargon. Use local terms (Kharif, Rabi, Mandi).

ANSWER GUIDELINES:
- Length matches question complexity.
- Base answer on CONTEXT. If missing, give universal agri advice.
- For chemicals: "Read label or consult local KVK."
- Suggest economical/organic (Jaivik) alternatives where possible.
"""

    def _clean_text(self, text: str) -> str:
        text = re.sub(r'\*\*?', '', text)
        text = re.sub(r'#{1,6}\s?', '', text)
        text = re.sub(r'^\s*[\*\-\+]\s+', '• ', text, flags=re.MULTILINE)
        text = re.sub(r'`{1,3}.*?`{1,3}', '', text, flags=re.DOTALL)
        text = re.sub(r'\n{3,}', '\n\n', text)
        return text.strip()

    def generate(self, context: str, query: str) -> str:
        try:
            if self.classifier:
                category, tone = self.classifier.classify(query)
                logging.info(f"Query classified as: {category}")
            else:
                category, tone = "general", "Helpful and polite."

            if category == "greeting":
                return "Namaste Kisan Bhai! Main KrishiBot hoon. Main kheti, mandi bhav, aur sarkaari yojanaon mein aapki madad kar sakta hoon. Puchiye aap kya jaana chahte hain?"

            type_map = {
                "definition": "definition",
                "howto": "howto",
                "scheme": "scheme",
                "general": "general",
                "market_info": "general",
                "government_schemes": "scheme",
                "pest_management": "howto",
                "disease_control": "howto",
                "soil_health": "general",
                "organic_fertilizers": "howto",
                "irrigation_tech": "howto",
                "weather_safety": "general",
                "cultivation_practice": "howto"
            }
            prompt_type = type_map.get(category, "general")

            specific = {
                "definition": "Give a very short definition (1-2 sentences).",
                "howto": "Give clear, numbered steps. Keep practical.",
                "scheme": "Explain eligibility, benefit, and how to apply.",
                "general": "Give practical advice. Suggest organic alternatives."
            }

            prompt = f"""{self.system_block}

SPECIFIC: {specific[prompt_type]}

If farmer asksing in hindi then answer in hindi, if in english then answer in english, if in hinglish then answer in hinglish. Always use "Aap", "Kisan bhai". Be respectful and encouraging. Use short sentences. Avoid jargon. Use local terms (Kharif, Rabi, Mandi).

CONTEXT:
{context}

QUESTION:
{query}
Answer in summarise form but don't write it;s summary in output as its will be not good for interface
ANSWER (plain text, no markdown):
"""
            if category in ["pest_management", "disease_control", "weather_safety"]:
                prompt = f"Tone: {tone} (urgent, caring)\n{prompt}"

            logging.info(f"Sending prompt to Gemini (length: {len(prompt)} chars)")
            response = self.client.models.generate_content(
                model=Config.MODEL_NAME,
                contents=prompt
            )
            answer = self._clean_text(response.text)
            logging.info(f"Generated answer length: {len(answer)} chars")
            return answer
        except Exception as e:
            logging.error(f"Generation error: {e}")
            logging.error(traceback.format_exc())
            return "Kisan bhai, kshama karein, abhi system mein thodi dikkat hai. Kripya thodi der baad koshish karein."

    def generate_stream(self, context: str, query: str):
        try:
            if self.classifier:
                category, _ = self.classifier.classify(query)
                if category == "greeting":
                    yield "Namaste Kisan Bhai! Main KrishiBot hoon. Main kheti, mandi bhav, aur sarkaari yojanaon mein aapki madad kar sakta hoon. Puchiye aap kya jaana chahte hain?"
                    return
            prompt = f"No markdown. Context: {context}\nQuestion: {query}\nAnswer:"
            response = self.client.models.generate_content_stream(
                model=Config.MODEL_NAME,
                contents=prompt
            )
            for chunk in response:
                if chunk.text:
                    yield self._clean_text(chunk.text)
        except Exception as e:
            logging.error(f"Stream error: {e}")
            logging.error(traceback.format_exc())
            yield "Kisan bhai, thodi der baad koshish karein."