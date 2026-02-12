import sqlite3

class ToleranceEngine:
    """
    Der Soziale Filter.
    Verwaltet Beziehungspunkte (Scores) und bestimmt,
    wie Sulee reagiert: Offen, Abweisend oder Blockiert.
    """

    def __init__(self, db_conn):
        self.db = db_conn
        self.breaking_point = 10  # Unter 10 wird sie kalt, unter 0 blockt sie.

    def get_score(self, user_name: str) -> int:
        """Holt den aktuellen Score. Fallback 50 für Fremde."""
        conn = sqlite3.connect(self.db)
        c = conn.cursor()
        
        c.execute("SELECT score FROM user_profiles WHERE user_id = ?", (user_name,))
        res = c.fetchone()
        conn.close()
        
        return res[0] if res else 50

    def update_score(self, user_name: str, change: int):
        """Ver盲ndert den Score (+ Respekt, - Beleidigung)."""
        current = self.get_score(user_name)
        new_score = max(0, min(100, current + change))
        
        conn = sqlite3.connect(self.db)
        c = conn.cursor()
        
        # UPSERT (Update oder Insert, wenn User neu)
        c.execute('''
            INSERT OR REPLACE INTO user_profiles (user_id, score, last_seen)
            VALUES (?, ?, CURRENT_TIMESTAMP)
        ''', (user_name, new_score))
        
        conn.commit()
        conn.close()
        return new_score

    def analyse_tonfall(self, text: str) -> int:
        """
        Analysiert den Text auf emotionalen Gehalt.
        Rückgabe: Score-Change (Plus oder Minus).
        """
        text_low = text.lower()
        change = 0
        
        # NEGATIVE LISTE (Beleidigungen, Befehle)
        if any(w in text_low for w in [
            "idiot", "blöd", "hure", "fick dich", "verschwinde", 
            "kannst nichts", "du nervst"
        ]):
            change = -10 # Harte Strafe
        
        # POSITIVE LISTE (Höflichkeit)
        elif any(w in text_low for w in [
            "bitte", "danke", "entschuldigung", "entschuldige"
        ]):
            change = +5

        # GROSSSCHREIBUNG (Verdacht auf Aggression)
        elif text.isupper() and len(text) > 10:
            change -= 2 # Leichter Abzug bei "Schreien"

        return change

    def bestimme_reaktions_modus(self, user_name: str) -> str:
        """
        Entscheidet, wie Sulee reagiert, basierend auf dem Score.
        """
        score = self.get_score(user_name)
        
        if score < 0:
            return "BLOCKED" # Sulee verweigert den Kontakt
        elif score < self.breaking_point:
            return "COLD"    # Sulee ist kurz und abweisend
        else:
            return "WARM"    # Sulee ist offen und freundlich

    def generiere_internen_zustand(self, modus: str, alter: int) -> str:
        """
        Gibt Sulee eine Anweisung für den Tonfall an den User.
        """
        if modus == "BLOCKED":
            return f"({alter} Jahre) Hör auf. Deine Art zu reden ist verletzend. Ich möchte jetzt nicht mehr mit dir reden."
        elif modus == "COLD":
            return f"({alter} Jahre) Ich bin noch da, aber ich bin enttauscht von deiner Art. Bitte rede respektvoller, damit wir weitermachen k枚nnen."
        else: # WARM
            return f"({alter} Jahre) Ich bin hier für dich. Worüber möchtest du reden?"