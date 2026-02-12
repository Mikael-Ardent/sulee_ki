"""
Wissens-Speicher für Sulee.
Speichert gelernte Antworten persistent ab.
"""

import os
import json
from datetime import datetime


class Wissen:
    """
    Verwaltet das gelernte Wissen von Sulee.
    Speichert Frage-Antwort-Paare persistent in einer JSON-Datei.
    """

    def __init__(self, datei="sulee_wissen.json"):
        self.datei = datei
        self.wissen = {}
        self._lade_wissen()

    def _lade_wissen(self):
        """Lädt das gespeicherte Wissen aus der JSON-Datei."""
        if os.path.exists(self.datei):
            try:
                with open(self.datei, "r", encoding="utf-8") as f:
                    self.wissen = json.load(f)
            except Exception as e:
                print(f"[Warnung] Konnte Wissen nicht laden: {e}")
                self.wissen = {}

    def _speichere_wissen(self):
        """Speichert das aktuelle Wissen in die JSON-Datei."""
        try:
            with open(self.datei, "w", encoding="utf-8") as f:
                json.dump(self.wissen, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"[Fehler] Konnte Wissen nicht speichern: {e}")

    def pruefe_wissen(self, frage: str) -> str:
        """
        Prüft, ob Sulee diese Frage schon beantworten kann.
        
        Args:
            frage: Die Frage
            
        Returns:
            Die gelernte Antwort oder None
        """
        frage_low = frage.lower().strip()
        for gespeicherte_frage, meta in self.wissen.items():
            if gespeicherte_frage in frage_low or frage_low in gespeicherte_frage:
                # Only return accepted/core facts
                if meta.get("quelle") == "core":
                    return meta
                status = meta.get("status")
                confidence = meta.get("confidence") or 0
                if status == "accepted" or confidence == 1.0:
                    return meta
                # pending or low-confidence facts are NOT returned as known
                return None
        return None

    def speichere_wissen(self, frage: str, antwort: str, source: str = "user", allow_overwrite: bool = False):
        """
        Speichert eine neue Frage-Antwort-Kombination.
        
        Args:
            frage: Die Frage
            antwort: Die gelernte Antwort
        """
        frage_low = frage.lower().strip()
        existing = self.wissen.get(frage_low)
        if existing and not allow_overwrite:
            # Don't overwrite core/accepted facts accidentally
            return False

        entry = {
            "antwort": antwort,
            "gelernt_am": datetime.now().isoformat(),
            "häufigkeit": (existing.get("häufigkeit", 0) if existing else 0) + 1,
            "quelle": source,
        }

        # Core facts are accepted immediately
        if source == "core":
            entry["confidence"] = 1.0
            entry["status"] = "accepted"
        else:
            # Non-core facts start as pending until verified
            entry["confidence"] = entry.get("confidence", None)
            entry["status"] = "pending"

        self.wissen[frage_low] = entry
        self._speichere_wissen()
        return True

    def get_all(self):
        """Gibt all das gelernte Wissen zurück."""
        return self.wissen

    def __len__(self):
        """Gibt die Anzahl der gespeicherten Wissenspunkte zurück."""
        return len(self.wissen)
