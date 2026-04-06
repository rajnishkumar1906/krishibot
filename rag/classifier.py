import numpy as np
from typing import Tuple

class QueryClassifier:
    """Advanced semantic router with 10 data-specific categories and humanized tones."""

    def __init__(self, embedding_model):
        # embedding_model is an instance of EmbeddingModel, which has a .model attribute
        # that is the HuggingFaceEndpointEmbeddings object.
        self.embedding = embedding_model.model
        self.categories = {
            "greeting": {
                "examples": [
                    "hi", "hello", "namaste", "ram ram", "thank you", "dhanyabad",
                    "shukriya", "good morning", "kaise ho", "thanks bhai"
                ],
                "tone": "Warm, welcoming, and very respectful."
            },
            "market_info": {
                "examples": [
                    "mandi price", "msp of wheat", "paddy rate", "enam registration",
                    "market fee", "sell crops", "bhav kya hai", "mandi tax", "cotton rate"
                ],
                "tone": "Professional and encouraging. Focus on the farmer's profit and hard work."
            },
            "government_schemes": {
                "examples": [
                    "pm kisan status", "fasal bima yojana", "kcc loan", "subsidy",
                    "pm kusum solar", "sarkari yojana", "apply for scheme", "paisa kab aayega"
                ],
                "tone": "Patient and helpful. Act like a guide through government paperwork."
            },
            "pest_management": {
                "examples": [
                    "stem borer", "brown plant hopper", "leaf folder", "aphids",
                    "whiteflies", "keeda lag gaya", "pest control", "yellow sticky traps"
                ],
                "tone": "Empathetic and urgent. Like a 'Doctor' for the crops."
            },
            "disease_control": {
                "examples": [
                    "early blight", "late blight", "tomato disease", "fungal infection",
                    "yellow leaves", "root rot", "leaf curl virus", "fungicide spray"
                ],
                "tone": "Supportive and diagnostic. Focus on healing the plant quickly."
            },
            "soil_health": {
                "examples": [
                    "soil test", "ph level", "acidic soil", "gypsum application",
                    "soil health card", "mitti ki janch", "black soil", "alluvial soil"
                ],
                "tone": "Practical and traditional. Focus on 'Dharti Maa' and long-term fertility."
            },
            "organic_fertilizers": {
                "examples": [
                    "jeevamrut recipe", "vermicompost", "panchagavya", "organic khad",
                    "cow dung manure", "dashparni ark", "neem coated urea", "jaivik kheti"
                ],
                "tone": "Nature-focused and sustainable. Encourage natural farming methods."
            },
            "irrigation_tech": {
                "examples": [
                    "drip irrigation", "venturi system", "sprinkler", "watering schedule",
                    "drip spacing", "fertigation", "water pump", "micro irrigation"
                ],
                "tone": "Technical yet simple. Focus on saving water and modern efficiency."
            },
            "weather_safety": {
                "examples": [
                    "hailstorm", "heavy rain", "drought", "heat wave", "barish se bachav",
                    "pala padna", "frost protection", "weather forecast"
                ],
                "tone": "Urgent and protective. Focus on immediate safety steps and relief."
            },
            "cultivation_practice": {
                "examples": [
                    "sowing time", "rice sri method", "harvesting tips", "seed treatment",
                    "wheat variety", "wheat sowing", "paddy nursery", "crop rotation"
                ],
                "tone": "Wise and instructive. Like a seasoned elder farmer sharing experience."
            }
        }

        # Precompute embeddings for all example sentences (once at startup)
        self.example_embeddings = {}
        for cat, data in self.categories.items():
            if data["examples"]:
                self.example_embeddings[cat] = np.array(self.embedding.embed_documents(data["examples"]))
            else:
                self.example_embeddings[cat] = np.array([])

    def classify(self, query: str) -> Tuple[str, str]:
        """Returns (category, tone) for the given query."""
        q_lower = query.lower().strip()

        # Fast path for short greetings (less than 30 characters)
        if any(g in q_lower for g in self.categories["greeting"]["examples"]) and len(q_lower) < 30:
            return "greeting", self.categories["greeting"]["tone"]

        # Embed the user query
        query_emb = np.array(self.embedding.embed_query(query))

        best_cat = "general"
        best_score = -1.0
        best_tone = "Helpful and polite."

        for cat, emb_matrix in self.example_embeddings.items():
            if cat == "greeting":
                continue
            if emb_matrix.shape[0] == 0:
                continue

            # Cosine similarity
            dots = np.dot(emb_matrix, query_emb)
            norms = np.linalg.norm(emb_matrix, axis=1) * np.linalg.norm(query_emb)
            scores = dots / (norms + 1e-8)
            max_score = float(np.max(scores))

            if max_score > best_score:
                best_score = max_score
                best_cat = cat
                best_tone = self.categories[cat]["tone"]

        # Threshold: 0.42 works well for these 10 categories
        if best_score > 0.42:
            return best_cat, best_tone
        else:
            return "general", "Friendly and supportive."