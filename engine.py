from .answer_engine import AnswerEngine
from .emotion_engine import EmotionEngine
from .growth_engine import GrowthEngine


class SuleeEngine:
    """
    Haupt-Engine, die alle Sub-Engines lädt und koordiniert.
    - AnswerEngine: Generiert Rohantworten basierend auf Frage-Kategorien
    - EmotionEngine: Färbt Antworten mit emotionaler Stimmung
    - GrowthEngine: Verwaltet Entwicklung, Erfahrung und Level
    """

    def __init__(self, suleeki):
        # Referenz auf die Hauptklasse SuleeKI
        self.suleeki = suleeki

        # Sub-Engines initialisieren
        self.answer_engine = AnswerEngine(suleeki)
        self.emotion_engine = EmotionEngine(suleeki)
        self.growth_engine = GrowthEngine(suleeki)

    # ---------------------------------------------------------
    # ÖFFENTLICHE SCHNITTSTELLE
    # ---------------------------------------------------------

    def generate_answer(self, frage: str) -> str:
        """
        Hauptzugangspunkt für alle Antworten.
        
        Ablauf:
        1. AnswerEngine generiert Rohantwort
        2. EmotionEngine färbt sie mit der aktuellen Stimmung
        3. GrowthEngine registriert die Interaktion
        
        Returns:
            str: Emotionsgefärbte Antwort
        """
        # Rohantwort generieren
        roh = self.answer_engine.generate_answer(frage)
        
        # Mit Stimmung färben
        gefärbt = self.emotion_engine.färbe_antwort(roh)
        
        # Erfahrung hinzufügen
        self.growth_engine.add_erfahrung(1)
        
        return gefärbt

    # ---------------------------------------------------------
    # STIMMUNGS-SCHNITTSTELLE
    # ---------------------------------------------------------

    def set_stimmung(self, stimmung: str):
        """Ändert Sulees aktuelle Stimmung."""
        self.emotion_engine.set_stimmung(stimmung)

    def get_stimmung(self) -> str:
        """Liefert Sulees aktuelle Stimmung."""
        return self.emotion_engine.get_stimmung()

    # ---------------------------------------------------------
    # WACHSTUMS-SCHNITTSTELLE
    # ---------------------------------------------------------

    def get_alter(self) -> int:
        """Liefert Sulees aktuelles Alter."""
        return self.growth_engine.get_alter()

    def set_alter(self, alter: int):
        """Setzt Sulees Alter."""
        self.growth_engine.set_alter(alter)

    def get_beschreibung_reife(self) -> str:
        """Liefert eine Beschreibung, wie reif Sulee wirkt."""
        return self.growth_engine.beschreibe_reifegrad()
