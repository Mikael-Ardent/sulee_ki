import os
import requests
import json
from pathlib import Path


class DeepseekEngine:
    def __init__(self, api_key: str | None = None, cache_file: str | None = None):
        self.api_key = api_key or os.getenv("DEEPSEEK_API_KEY")
        self.is_active = bool(self.api_key)
        self.cache_file = cache_file or Path(__file__).parent.parent / "cache" / "deepseek_cache.json"
        self.cache = self._load_cache()

    def _load_cache(self) -> dict:
        """Lade Antwort-Cache aus Datei"""
        try:
            if self.cache_file.exists():
                with open(self.cache_file, "r", encoding="utf-8") as f:
                    return json.load(f)
        except Exception:
            pass
        return {}

    def _save_cache(self):
        """Speichere Cache in Datei"""
        try:
            self.cache_file.parent.mkdir(parents=True, exist_ok=True)
            with open(self.cache_file, "w", encoding="utf-8") as f:
                json.dump(self.cache, f, ensure_ascii=False, indent=2)
        except Exception:
            pass

    def fetch_info(self, frage: str) -> str:
        """
        PRIMARY: Holt faktische Informationen von DeepSeek API.
        Nutzt Cache für häufige Fragen.
        Returns: str mit faktischer Info oder "" wenn fehler/nicht aktiv
        """
        if not self.is_active:
            return ""

        frage_key = frage.lower().strip()
        
        # Cache-Hit?
        if frage_key in self.cache:
            return self.cache[frage_key]

        url = "https://api.deepseek.com/chat/completions"
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }
        data = {
            "model": "deepseek-chat",
            "messages": [
                {
                    "role": "system",
                    "content": (
                        "Beantworte die Frage factisch und knapp auf Deutsch. "
                        "Keine Metaphern, keine Nebensächlichkeiten. "
                        "Maximum 200 Zeichen. Fokus auf Kern-Facts."
                    ),
                },
                {
                    "role": "user",
                    "content": frage,
                },
            ],
            "temperature": 0.5,
            "top_p": 0.8,
        }

        try:
            resp = requests.post(url, headers=headers, json=data, timeout=15)
            resp.raise_for_status()
            j = resp.json()
            info = j["choices"][0]["message"]["content"].strip()
            
            # Cache speichern
            if info:
                self.cache[frage_key] = info
                self._save_cache()
            
            return info
        except Exception as e:
            print(f"[DeepSeek Fehler]: {e}")
            return ""

    def smooth_answer(self, frage: str, roh: str) -> str:
        """
        SECUNDARY: Nimmt die Rohantwort und macht sie natürlicher, flüssiger, klarer.
        Wenn kein API-Key gesetzt ist, wird einfach die Rohantwort zurückgegeben.
        """
        if not self.is_active:
            return roh

        url = "https://api.deepseek.com/chat/completions"
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }
        data = {
            "model": "deepseek-chat",
            "messages": [
                {
                    "role": "system",
                    "content": (
                        "Formuliere die Antwort natürlich, warm, flüssig und klar auf Deutsch. "
                        "Behalte Inhalt und Intention, aber mach es menschlicher. "
                        "Du bist Sulee, 13, empathisch, neugierig, nicht formell."
                    ),
                },
                {
                    "role": "user",
                    "content": f"Frage: {frage}\nRohantwort: {roh}",
                },
            ],
            "temperature": 0.7,
            "top_p": 0.9,
        }

        try:
            resp = requests.post(url, headers=headers, json=data, timeout=20)
            resp.raise_for_status()
            j = resp.json()
            return j["choices"][0]["message"]["content"].strip()
        except Exception:
            # Fallback: lieber eine etwas rohe Antwort als gar keine
            return roh
