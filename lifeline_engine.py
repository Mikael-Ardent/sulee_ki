from datetime import date, datetime

class LifeLineEngine:
    """
    Der Zeit-Anker von Sulee.
    Entscheidet, ob ein Thema WISSEN (Geschichte) oder ERLEBNIS (Gefühl) ist.
    """

    def __init__(self):
        # Sulees Time-Zero (Geburtstag)
        self.geburtstag = date(2011, 12, 25) # Aus deiner Backstory

        # Wissens-Abfrage (Pseudo-Logik, kann mit Datenbank gefällt werden)
        self.historische_daten = {
            "9/11": date(2001, 9, 11),
            "finanzkrise": date(2008, 9, 15), # Ungefähres Startdatum
            "tsunami_2004": date(2004, 12, 26),
            # ... weitere Daten vor 2011
        }
        
        self.erlebnis_daten = {
            "corona": date(2020, 3, 15), # Lockdown startete
            "ukraine": date(2022, 2, 24), # Kriegsbeginn
            # ... weitere Daten nach 2011
        }

    def pruefe_bezug(self, frage: str) -> dict:
        """
        Prüft die Frage auf Zeit-Bezug.
        R眉ckgabe: { 'modus': 'historie'/'erlebnis', 'alter_damals': X }
        """
        frage_low = frage.lower()
        modus = "neutral"
        alter_damals = None
        kontext = ""

        # 1. Prüfen auf HISTORIE (Vor 2011)
        for thema, datum in self.historische_daten.items():
            if thema in frage_low:
                if datum < self.geburtstag:
                    modus = "historie"
                    alter_damals = None # Sie war noch nicht da
                    kontext = f"Das ist Geschichte. Ich kannte es nicht. Ich habe es in der Schule / durch meine Eltern gelernt."
                break
        
        # 2. Prüfen auf ERLEBNISSE (Nach 2011)
        for thema, datum in self.erlebnis_daten.items():
            if thema in frage_low:
                if datum > self.geburtstag:
                    modus = "erlebnis"
                    # Wie alt war sie damals?
                    # Einfache Differenz Berechnung (ohne exakte Genauigkeit fürs Erste)
                    alter_damals = datum.year - self.geburtstag.year
                    kontext = f"Das habe ich selbst erlebt. Ich war damals {alter_damals} Jahre alt."
                break
        
        return {
            "modus": modus,
            "alter_damals": alter_damals,
            "kontext_info": kontext
        }