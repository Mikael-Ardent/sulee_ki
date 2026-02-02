"""
Zustand & Status Manager für Sulee.
Verwaltet persistente Zustände wie Hunger, Energie und Tages-Statistiken.
"""

import os
import json
from datetime import datetime, date


class StatusManager:
    """
    Verwaltet Sulees interne Zustände (Hunger, Energie, etc.)
    und speichert diese persistent.
    """

    def __init__(self, datei="sulee_status.json"):
        self.datei = datei
        self.status = {
            "hunger": 30,  # 0 = satt, 100 = verhungert
            "energie": 90,  # 0 = schläfrig, 100 = wach
            "datum_aktualisiert": date.today().isoformat(),
            "tages_interaktionen": 0,
            "wartende_anfrage": None,
            "bild_gezaehlt_heute": False,
        }
        self._lade_status()

    def _lade_status(self):
        """Lädt den gespeicherten Status."""
        if os.path.exists(self.datei):
            try:
                with open(self.datei, "r", encoding="utf-8") as f:
                    geladen = json.load(f)
                    self.status.update(geladen)
                    
                    # Reset Tages-Statistiken wenn neuer Tag
                    if geladen.get("datum_aktualisiert") != date.today().isoformat():
                        self.status["tages_interaktionen"] = 0
                        self.status["bild_gezaehlt_heute"] = False
                        self.status["datum_aktualisiert"] = date.today().isoformat()
                        self._speichere_status()
            except Exception as e:
                print(f"[Warnung] Konnte Status nicht laden: {e}")

    def _speichere_status(self):
        """Speichert den Status persistent."""
        try:
            with open(self.datei, "w", encoding="utf-8") as f:
                json.dump(self.status, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"[Fehler] Konnte Status nicht speichern: {e}")

    def set_hunger(self, wert: int):
        """Setzt den Hunger-Level (0-100)."""
        self.status["hunger"] = max(0, min(100, wert))
        self._speichere_status()

    def set_energie(self, wert: int):
        """Setzt das Energie-Level (0-100)."""
        self.status["energie"] = max(0, min(100, wert))
        self._speichere_status()

    def add_hunger(self, menge: int):
        """Addiert zum Hunger."""
        self.set_hunger(self.status["hunger"] + menge)

    def add_energie(self, menge: int):
        """Addiert zur Energie."""
        self.set_energie(self.status["energie"] + menge)

    def get_hunger_text(self) -> str:
        """Gibt eine Beschreibung des Hunger-Status."""
        h = self.status["hunger"]
        if h > 60:
            return "sehr hungrig 🤤"
        elif h > 30:
            return "ein bisschen hungrig 🍎"
        else:
            return "satt 😊"

    def get_energie_text(self) -> str:
        """Gibt eine Beschreibung des Energie-Status."""
        e = self.status["energie"]
        if e < 30:
            return "total müde 😴"
        elif e < 60:
            return "ein bisschen müde 😑"
        else:
            return "munter 😊"

    def register_interaktion(self):
        """Registriert eine neue Interaktion."""
        self.status["tages_interaktionen"] = self.status.get("tages_interaktionen", 0) + 1
        self._speichere_status()

    def get(self, key: str, default=None):
        """Gibt einen Status-Wert zurück."""
        return self.status.get(key, default)

    def set(self, key: str, value):
        """Setzt einen Status-Wert."""
        self.status[key] = value
        self._speichere_status()

    def __repr__(self):
        return f"<StatusManager hunger={self.status['hunger']} energie={self.status['energie']}>"
