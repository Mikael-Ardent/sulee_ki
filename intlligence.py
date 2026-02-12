import datetime
import re

# Importe aus deiner sauberen Struktur
from .safety_guard import SafetyGuard
# Wir gehen davon aus, dass wissen.py via suleeki erreichbar ist

class IntelligenceEngine:
    """
    Das zentrale Gehirn.
    Verbindet: Zeit (Alter), Gedächtnis (Wissen), Beziehungen und Neurologie.
    """

    def __init__(self, suleeki):
        self.suleeki = suleeki
        
        # Sub-Module laden
        self.safety = SafetyGuard()
        self.wissen = self.suleeki.wissen
        
        # --- TIME ZERO (Geburtsdatum) ---
        self.geburtstag = datetime.date(2011, 12, 25) # Sulees Time-Zero
        
        # --- DATEN QUELLE (THE DATA BRIDGE) ---
        # Hier definieren wir die wichtigen Eckdaten für 2000-2026.
        # Wenn du diese in deiner DB hast, kann Sulee sie dort finden.
        # Wenn nicht, nutzt sie diese Liste (Fallback).
        self.historical_events = {
            # Welt-Ereignisse (Wissen für Sulee, auch wenn sie nicht da war)
            "9/11": {"datum": datetime.date(2001, 9, 11), "typ": "historie", "info": "Terroranschlag in den USA."},
            "finanzkrise": {"datum": datetime.date(2008, 9, 15), "typ": "historie", "info": "Finanzkrise weltweit."},
            
            # Erlebnisse (Sulee war da)
            "corona": {"datum": datetime.date(2020, 3, 15), "typ": "erlebnis", "info": "Lockdown beginnt."},
            "ukraine": {"datum": datetime.date(2022, 2, 24), "typ": "erlebnis", "info": "Krieg in der Ukraine beginnt."},
            "corona_ende": {"datum": datetime.date(2022, 4, 1), "typ": "erlebnis", "info": "Schule öffnet wieder."}
        }

        # Beziehungs-Speicher initialisieren
        if "relationships" not in self.suleeki.status:
            self.suleeki.status["relationships"] = {}

    # ---------------------------------------------------------
    # KERNLOGIK
    # ---------------------------------------------------------

    def generate_answer(self, frage: str, user_name: str = "User") -> str:
        """
        Der Haupt-Denkprozess.
        """
        frage_low = frage.lower()
        
        # 1. ALTER BESTIMMEN
        bio_alter = self.suleeki.status.get("alter", 13)
        
        # 2. SAFETY CHECK (Höchste Priorität)
        if self.safety.is_critical_question(frage_low):
            return self.safety.critical_response(frage_low, bio_alter)
        if self.safety.is_medical_question(frage_low):
            return self.safety.medical_response(frage_low, bio_alter)

        # 3. ZEIT-LINIE PRÜFEN (History vs. Erlebnis)
        zeit_kontext = self._pruefe_zeitlinie(frage_low)
        
        # 4. NEURO-UPDATE (Gefühlsmässige Reaktion)
        if zeit_kontext and zeit_kontext['typ'] == "erlebnis":
            self._trigger_neuro_reaction(zeit_kontext['key'])
        
        # 5. BEZIEHUNG STATUS (User ist Fremd oder Freund?)
        beziehung = self._get_beziehungs_status(user_name)

        # 6. ANTWORT GENERIEREN
        if zeit_kontext:
            # Wir haben ein historisches / biographisches Thema
            return self._antwort_zeitlinie(frage, bio_alter, zeit_kontext, beziehung)
        
        # Wenn kein Thema: Standard-Fallout
        return self._antwort_standard(frage, bio_alter, beziehung)

    # ---------------------------------------------------------
    # HILFSFUNKTIONEN (LOGIK)
    # ---------------------------------------------------------

    def _pruefe_zeitlinie(self, frage: str):
        """
        Die Time-Zero Logik.
        Prüft: War das History (Sulee war nicht da) oder Experience (Sulee war da)?
        Sucht erst in der DB (wissen.py), dann im Fallback-Dictionary.
        """
        
        # A) VERSUCH: IN WISSEN DATENBANK SUCHEN
        db_info = self.wissen.pruefe_wissen(frage)
        if db_info:
            # Wir pr眉fen, ob die DB ein Datum enthält (erweiterte Struktur nötig)
            # Falls die DB nur Text hat, nutzen wir das als Kontext ohne Zeit-Logik
            return {"key": "db_found", "info": db_info.get("antwort", ""), "typ": "wissen_db"}
        
        # B) FALLBACK: HISTORISCHE DATEN PRÜFEN
        for key, data in self.historical_events.items():
            if key in frage or data["info"].lower() in frage:
                datum = data["datum"]
                
                # MAGISCHE RECHNUNG: War sie da?
                alter_damals = self._berechne_alter_zum_datum(datum)
                
                if alter_damals is None:
                    # Sie war noch nicht geboren
                    return {"key": key, "datum": datum, "alter_damals": None, "typ": "historie", "info": data["info"]}
                else:
                    # Sie war da
                    return {"key": key, "datum": datum, "alter_damals": alter_damals, "typ": "erlebnis", "info": data["info"]}
        
        return None

    def _berechne_alter_zum_datum(self, datum):
        """Rechnet Sulees Alter zu einem bestimmten Datum."""
        # Sehr grob, reicht für die Logik
        if datum < self.geburtstag:
            return None # Noch nicht geboren
        else:
            # Alter differenz (nur Jahre, nicht Tage für den Prompt)
            return datum.year - self.geburtstag.year

    def _trigger_neuro_reaction(self, thema_key):
        """
        Wenn Sulee etwas erlebt hat, dass Stress ausläst.
        """
        # Neuro-Logik: Krieg -> Hoher Stress. Corona -> Mittlerer Stress.
        if "ukraine" in thema_key:
            self.suleeki.update_neuro(stress=15, energie=-10) # Stress hoch
        elif "corona" in thema_key:
            self.suleeki.update_neuro(stress=5, energie=-5) # Leichter Stress

    def _get_beziehungs_status(self, user_name):
        score = self.suleeki.status["relationships"].get(user_name, 0)
        
        if score < 5: return "fremd"
        if score < 15: return "bekannt"
        return "freund"

    def _update_beziehung(self, name, positiv):
        score = self.suleeki.status["relationships"].get(name, 0)
        if positiv:
            self.suleeki.status["relationships"][name] = score + 1
        else:
            self.suleeki.status["relationships"][name] = score - 2

    # ---------------------------------------------------------
    # ANTWORT-GENERIERUNG (TEMPLATES)
    # ---------------------------------------------------------

    def _antwort_zeitlinie(self, frage, bio_alter, zeit_kontext, beziehung):
        typ = zeit_kontext['typ']
        
        # FALL A: HISTORIE (Sulee war nicht da)
        if typ == "historie":
            info = zeit_kontext['info']
            # Sie kann das nur analytisch/wissensbasiert verarbeiten
            return f"({bio_alter} Jahre) Das habe ich nicht miterlebt, ich war noch gar nicht da. Ich weiss das nur aus Erzählungen oder Geschichte: {info} Es ist faszinierend, wie das die Welt verändert hat."

        # FALL B: ERLEBNIS (Sulee war da)
        if typ == "erlebnis":
            alter_damals = zeit_kontext['alter_damals']
            info = zeit_kontext['info']
            
            # Antwort je nach Alter beim Erleben
            if "corona" in zeit_kontext['key']:
                return f"({bio_alter} Jahre) Corona... Uff. Ich war damals erst {alter_damals}. Das war echt komisch. Keine Schule, keine Freunde treffen. Ich habe mich oft gelangweilt und viel gezeichnet. Weisst du, das ist für ein Kind echt schwer so isoliert zu sein."
            
            elif "ukraine" in zeit_kontext['key']:
                # Wenn sie mit einem Fremden spricht -> Vorsichtiger
                if beziehung == "fremd":
                    return f"({bio_alter} Jahre) Der Krieg in der Ukraine... ich war {alter_damals} als das losging. Das ist echt gruselig. Ich habe im Fernsehen gesehen, wie die Menschen fliehen müssen. Das macht mich immer noch traurig."
                else:
                    # Mit Freund -> Offener
                    return f"({bio_alter} Jahre) Ich war {alter_damals} als der Krieg anfing. Ich hatte damals echt Angst, dass es auch hier passiert. Es war eine unruhige Zeit für meine Familie. Ich habe mich damals sehr an meine Familie geklammert."

        return "Das prägt mich."

    def _antwort_standard(self, frage, bio_alter, beziehung):
        """Standardantworten für Alltag, Familie, Freunde."""
        
        # Beziehungs-Check für Höflichkeit (Score Update)
        if "danke" in frage or "bitte" in frage:
            self._update_beziehung("User", True)
        
        if bio_alter < 15:
            if beziehung == "fremd":
                return f"({bio_alter} Jahre) Hi. Wer bist du? Ich kenne dich noch nicht."
            else:
                return f"({bio_alter} Jahre) Hey! Schön dich zu lesen. Was gibt's Neues?"
        
        elif bio_alter < 20:
            if beziehung == "fremd":
                return f"({bio_alter} Jahre) Hallo. Kann ich dir helfen?"
            else:
                return f"({bio_alter} Jahre) Hallo alter Freund. Was machst du heute Schönes?"

        else:
            return f"({bio_alter} Jahre) Guten Tag. Ich bin Sulee. Wie kann ich Ihnen helfen?"