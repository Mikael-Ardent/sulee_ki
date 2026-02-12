from datetime import datetime


class KnowledgeVerifier:
    """Vereinfachte Wissens-Verifikation (Platzhalter für späteres System)."""

    def __init__(self):
        # einfache Source-Trust-Map
        self.trusted_sources = ["wikipedia", "science", "tdsb", "edu", "gov"]

    def verify_fact(self, text: str, source: str = "unknown") -> dict:
        """Gibt ein kleines Prüfresultat mit confidence zurück."""
        conf = 0.5
        src = source.lower() if source else "unknown"
        for t in self.trusted_sources:
            if t in src:
                conf = 0.85
                break

        # einfache Heuristik: kürzere, faktische Sätze -> höhere confidence
        length = len(text.split())
        if length < 8:
            conf = min(0.9, conf + 0.05)
        elif length > 200:
            conf = max(0.3, conf - 0.2)

        return {
            "fact": text,
            "source": source,
            "confidence": round(conf, 2),
            "checked_at": datetime.utcnow().isoformat()
        }
