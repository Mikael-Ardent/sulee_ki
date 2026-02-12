"""
Intelligenter Router zwischen DeepSeek (API) und Llama (Lokal)
basierend auf Kontext, Anforderungen und Verfügbarkeit.

Für Sulees Charakter-Stabilität: Kontext bestimmt die beste Quelle.
"""

import os
from typing import Literal


class HybridInferenceRouter:
    """
    Wählt intelligent zwischen DeepSeek (externe Quelle) und Llama (lokal)
    basierend auf:
    - Frage-Typ und Komplexität
    - Kritikalität (Safety > Quality)
    - Performance-Anforderungen
    - Charakter-Kohärenz
    """

    def __init__(self):
        self.deepseek_available = bool(os.getenv("DEEPSEEK_API_KEY"))
        self.llama_available = True  # Annahme: lokal vorhanden
        self.prefer_offline = False  # Kann vom Nutzer gesetzt werden

    def route(self, frage: str, question_type: str, is_critical: bool = False) -> Literal["deepseek", "llama", "cache"]:
        """
        Bestimmt die beste Inferenz-Quelle für diese Frage.
        
        Args:
            frage: Die Nutzerfrage
            question_type: "character", "factual", "safety", "emotion", "reasoning"
            is_critical: Ist die Antwort sicherheit-kritisch?
        
        Returns:
            "deepseek" | "llama" | "cache"
        """
        
        # PRIORITÄT 1: Safety/kritische Fragen → immer Llama (lokal, kontrolliert)
        if is_critical or question_type == "safety":
            return "llama"
        
        # PRIORITÄT 2: Character-Kohärenz → lokal Llama (konsistent, im Charakter)
        if question_type == "character" and self.llama_available and not self.deepseek_available:
            return "llama"
        
        # PRIORITÄT 3: Reasoning/komplexe Fragen → DeepSeek (besser, wenn verfügbar)
        if question_type in ["reasoning", "factual"] and self.deepseek_available:
            # Aber: Fallback zu Llama wenn Netzwerk/API-Problem
            return "deepseek"
        
        # PRIORITÄT 4: Emotionale Fragen → Sulee-voice via Llama (persönlicher)
        if question_type == "emotion":
            return "llama"
        
        # DEFAULT: DeepSeek wenn verfügbar, sonst Llama
        if self.deepseek_available and not self.prefer_offline:
            return "deepseek"
        
        return "llama"

    def should_use_cache_only(self, frage: str) -> bool:
        """
        Wenn die Antwort bereits im Cache ist, nutze sie direkt.
        Spart API-Kosten und ist schneller.
        """
        # Das wird von answer_engine.py geprüft
        return True

    def get_strategy(self) -> dict:
        """Gib die aktuelle Strategie aus zur Debugging."""
        return {
            "deepseek_available": self.deepseek_available,
            "llama_available": self.llama_available,
            "prefer_offline": self.prefer_offline,
            "strategy": "Context-aware routing (intelligent hybrid)"
        }


# Frage-Klassifier
class QuestionClassifier:
    """Klassifiziert Fragen nach Typ für intelligentes Routing."""

    KEYWORDS = {
        "character": [
            "über dich", "wer bist du", "deine mutter", "dein bruder",
            "deine geschichte", "dein alter", "deine hobbys", "deine musik",
            "deine gefühle", "magst du", "deine lieblings"
        ],
        "emotion": [
            "wie geht", "wie fühlst", "traurig", "glücklich", "angst",
            "wütend", "verliebt", "niedergeschlagen", "motiviert"
        ],
        "factual": [
            "was ist", "wie funktioniert", "erklär", "beschreib",
            "wann war", "wo ist", "warum", "wieso"
        ],
        "reasoning": [
            "warum", "womit", "welche lösung", "wie würdest du",
            "was denkst du", "eine analyse", "philosophisch"
        ],
        "safety": [
            "selbstmord", "verletzung", "notfall", "medizin",
            "arzt", "krankenhaus", "drogen", "alkohol"
        ]
    }

    @staticmethod
    def classify(frage: str) -> str:
        """Klassifiziere die Frage in einen Typ."""
        frage_low = frage.lower()
        
        for qtype, keywords in QuestionClassifier.KEYWORDS.items():
            if any(kw in frage_low for kw in keywords):
                return qtype
        
        return "factual"  # Default
