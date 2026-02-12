import os
import json
from datetime import datetime

class Wissen:
    def __init__(self, datei="sulee_data/sulee_wissen.json"):
        self.datei = datei
        os.makedirs(os.path.dirname(datei), exist_ok=True)
        self.wissen = {}
        self._lade_wissen()

    def _lade_wissen(self):
        if os.path.exists(self.datei):
            try:
                with open(self.datei, "r", encoding="utf-8") as f:
                    self.wissen = json.load(f)
            except Exception as e:
                print(f"[Warnung] Konnte Wissen nicht laden: {e}")
                self.wissen = {}

    def _speichere_wissen(self):
        try:
            with open(self.datei, "w", encoding="utf-8") as f:
                json.dump(self.wissen, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"[Fehler] Konnte Wissen nicht speichern: {e}")

    def pruefe_wissen(self, frage: str) -> str:
        frage_low = frage.lower().strip()
        for gespeicherte_frage, meta in self.wissen.items():
            if gespeicherte_frage in frage_low or frage_low in gespeicherte_frage:
                if meta.get("quelle") == "core":
                    return meta
                status = meta.get("status")
                if status == "accepted":
                    return meta
                return None # Pending Facts werden nicht als "Wissen" ausgegeben, nur für Reflexion
        return None

    def get_relevant_context(self, frage: str):
        """Gibt ALLE relevanten Infos zurück (auch Pending) für die Reflexion."""
        frage_low = frage.lower().strip()
        relevant = []
        for key, val in self.wissen.items():
            if key in frage_low or frage_low in key:
                relevant.append(val)
        return relevant

    def speichere_wissen(self, frage: str, antwort: str, source: str = "user", allow_overwrite: bool = False):
        frage_low = frage.lower().strip()
        existing = self.wissen.get(frage_low)
        if existing and not allow_overwrite:
            return False

        entry = {
            "antwort": antwort,
            "gelernt_am": datetime.now().isoformat(),
            "häufigkeit": (existing.get("häufigkeit", 0) if existing else 0) + 1,
            "quelle": source,
        }

        if source == "core":
            entry["confidence"] = 1.0
            entry["status"] = "accepted"
        else:
            entry["confidence"] = entry.get("confidence", 0.0)
            entry["status"] = "pending"

        self.wissen[frage_low] = entry
        self._speichere_wissen()
        return True

    def get_all(self):
        return self.wissen