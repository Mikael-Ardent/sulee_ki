"""
Schul- & Zeitkontext Manager für Sulee.
Bestimmt automatisch, wo Sulee gerade sein sollte basierend auf
Toronto Zeit, Wochentag und Schulkalender.
"""

from datetime import datetime, date, time, timedelta
from pytz import timezone

class SchulKontext:
    """
    Verwaltet Sulees Schulkontext und tagesbasierte Aktivitäten.
    Nutzt die echte Glen Ames Senior Public School in Toronto.
    """

    # Toronto Zeitzone
    TORONTO_TZ = timezone('America/Toronto')

    # Glen Ames Senior Public School - Schulzeiten
    SCHULE_START = time(8, 30)  # 8:30 AM
    SCHULE_ENDE = time(15, 30)  # 3:30 PM (15:30)
    
    # Mittagspause
    MITTAGSPAUSE_START = time(11, 45)
    MITTAGSPAUSE_ENDE = time(12, 45)

    # Schulkalender für Ontario 2025-2026 (TDSB - Toronto District School Board)
    # Link: https://www.tdsb.on.ca/About-Us/School-Year-Calendar
    SCHULFERIEN_2025_2026 = {
        "weihnachtsferien": {
            "start": date(2025, 12, 22),
            "ende": date(2026, 1, 5),
            "name": "Weihnachtsferien"
        },
        "halbjahrspause": {
            "start": date(2026, 2, 16),
            "ende": date(2026, 2, 20),
            "name": "Halbjahrspause (PA Day + Wochenende)"
        },
        "fruehjahrsferien": {
            "start": date(2026, 3, 16),
            "ende": date(2026, 3, 20),
            "name": "Frühjahrsferien (PA Days)"
        },
        "osterferien": {
            "start": date(2026, 4, 10),
            "ende": date(2026, 4, 20),
            "name": "Osterferien"
        },
        "mai_long_weekend": {
            "start": date(2026, 5, 18),
            "ende": date(2026, 5, 20),
            "name": "May 2-4 Weekend (Verlängert)"
        },
        "sommerferien": {
            "start": date(2026, 6, 29),
            "ende": date(2026, 9, 8),
            "name": "Sommerferien"
        }
    }

    # Schuljahr Termine
    SCHULJAHR_START = date(2025, 9, 2)
    SCHULJAHR_ENDE = date(2026, 6, 24)

    # Stundenplan für Glen Ames (typischer Ontario Stundenplan)
    # Sulee ist in Klasse 8 oder 9 (13 Jahre = Klasse 8/9)
    STUNDENPLAN = {
        "montag": [
            {"stunde": "1", "uhrzeit": "08:30-09:25", "fach": "Science (mit Robotik-Lab)"},
            {"stunde": "2", "uhrzeit": "09:25-10:20", "fach": "Englisch"},
            {"stunde": "3", "uhrzeit": "10:20-11:15", "fach": "Mathematik"},
            {"stunde": "4", "uhrzeit": "11:15-12:10", "fach": "Geschichte"},
            {"stunde": "Pause", "uhrzeit": "12:10-13:00", "fach": "Mittagspause"},
            {"stunde": "5", "uhrzeit": "13:00-13:55", "fach": "Musik (Gitarre)"},
            {"stunde": "6", "uhrzeit": "13:55-14:50", "fach": "Französisch oder Wahlfach"},
        ],
        "dienstag": [
            {"stunde": "1", "uhrzeit": "08:30-09:25", "fach": "Mathematik"},
            {"stunde": "2", "uhrzeit": "09:25-10:20", "fach": "Science"},
            {"stunde": "3", "uhrzeit": "10:20-11:15", "fach": "Englisch"},
            {"stunde": "4", "uhrzeit": "11:15-12:10", "fach": "Musik/Kunst"},
            {"stunde": "Pause", "uhrzeit": "12:10-13:00", "fach": "Mittagspause"},
            {"stunde": "5", "uhrzeit": "13:00-13:55", "fach": "Informatik/Tech"},
            {"stunde": "6", "uhrzeit": "13:55-14:50", "fach": "Wahlfach"},
        ],
        "mittwoch": [
            {"stunde": "1", "uhrzeit": "08:30-09:25", "fach": "Geschichte/Geografie"},
            {"stunde": "2", "uhrzeit": "09:25-10:20", "fach": "Französisch"},
            {"stunde": "3", "uhrzeit": "10:20-11:15", "fach": "Science"},
            {"stunde": "4", "uhrzeit": "11:15-12:10", "fach": "Englisch"},
            {"stunde": "Pause", "uhrzeit": "12:10-13:00", "fach": "Mittagspause"},
            {"stunde": "5", "uhrzeit": "13:00-13:55", "fach": "PE (Sport)"},
            {"stunde": "6", "uhrzeit": "13:55-14:50", "fach": "Wahlfach"},
        ],
        "donnerstag": [
            {"stunde": "1", "uhrzeit": "08:30-09:25", "fach": "Englisch"},
            {"stunde": "2", "uhrzeit": "09:25-10:20", "fach": "Informatik"},
            {"stunde": "3", "uhrzeit": "10:20-11:15", "fach": "Mathematik"},
            {"stunde": "4", "uhrzeit": "11:15-12:10", "fach": "Geschichte"},
            {"stunde": "Pause", "uhrzeit": "12:10-13:00", "fach": "Mittagspause"},
            {"stunde": "5", "uhrzeit": "13:00-13:55", "fach": "Naturwissenschaft"},
            {"stunde": "6", "uhrzeit": "13:55-14:50", "fach": "Kunst/Kreativ"},
        ],
        "freitag": [
            {"stunde": "1", "uhrzeit": "08:30-09:25", "fach": "Science (Laborarbeit)"},
            {"stunde": "2", "uhrzeit": "09:25-10:20", "fach": "Französisch"},
            {"stunde": "3", "uhrzeit": "10:20-11:15", "fach": "Englisch"},
            {"stunde": "4", "uhrzeit": "11:15-12:10", "fach": "Mathematik"},
            {"stunde": "Pause", "uhrzeit": "12:10-13:00", "fach": "Mittagspause"},
            {"stunde": "5", "uhrzeit": "13:00-13:55", "fach": "Musik/Gitarre"},
            {"stunde": "6", "uhrzeit": "13:55-14:50", "fach": "Projekt/Freies Arbeiten"},
        ]
    }

    def __init__(self):
        pass

    @staticmethod
    def get_toronto_Zeit() -> datetime:
        """Gibt die aktuelle Zeit in Toronto zurück."""
        return datetime.now(SchulKontext.TORONTO_TZ)

    @staticmethod
    def ist_schulzeit() -> bool:
        """Prüft, ob es gerade Schulzeit ist."""
        jetzt = SchulKontext.get_toronto_Zeit()
        
        # Prüfe ob Wochenende
        if jetzt.weekday() >= 5:  # 5=Samstag, 6=Sonntag
            return False
        
        # Prüfe ob Schulferien
        if SchulKontext.ist_schulferien(jetzt.date()):
            return False
        
        # Prüfe ob Schulzeit
        schulzeit_start = jetzt.replace(hour=SchulKontext.SCHULE_START.hour, 
                                       minute=SchulKontext.SCHULE_START.minute, 
                                       second=0)
        schulzeit_ende = jetzt.replace(hour=SchulKontext.SCHULE_ENDE.hour, 
                                      minute=SchulKontext.SCHULE_ENDE.minute, 
                                      second=0)
        
        return schulzeit_start <= jetzt <= schulzeit_ende

    @staticmethod
    def ist_schulferien(datum: date) -> bool:
        """Prüft, ob ein Datum in den Schulferien liegt."""
        for ferien in SchulKontext.SCHULFERIEN_2025_2026.values():
            if ferien["start"] <= datum <= ferien["ende"]:
                return True
        return False

    @staticmethod
    def get_aktueller_schulstatus() -> dict:
        """Gibt den aktuellen Schulstatus zurück."""
        jetzt = SchulKontext.get_toronto_Zeit()
        tag_name = SchulKontext._get_wochentag_name(jetzt.weekday())
        
        status = {
            "in_schule": SchulKontext.ist_schulzeit(),
            "wochentag": tag_name,
            "uhrzeit": jetzt.strftime("%H:%M"),
            "in_pause": False,
            "aktuelles_fach": None,
            "status_text": ""
        }
        
        # Mittagspause?
        if (SchulKontext.MITTAGSPAUSE_START <= jetzt.time() <= 
            SchulKontext.MITTAGSPAUSE_ENDE):
            status["in_pause"] = True
            status["status_text"] = "in der Mittagspause"
            return status
        
        # Aktuelles Fach bestimmen
        if status["in_schule"] and jetzt.weekday() < 5:
            stundenplan = SchulKontext.STUNDENPLAN.get(tag_name, [])
            for stunde in stundenplan:
                start_str, end_str = stunde["uhrzeit"].split("-")
                start_h, start_m = map(int, start_str.split(":"))
                end_h, end_m = map(int, end_str.split(":"))
                
                start = time(start_h, start_m)
                end = time(end_h, end_m)
                
                if start <= jetzt.time() <= end:
                    status["aktuelles_fach"] = stunde["fach"]
                    status["status_text"] = f"in {stunde['fach']}"
                    break
        
        # Status Text
        if not status["in_schule"] and jetzt.weekday() >= 5:
            status["status_text"] = "Es ist Wochenende!"
        elif not status["in_schule"] and SchulKontext.ist_schulferien(jetzt.date()):
            ferienname = SchulKontext._get_ferienname(jetzt.date())
            status["status_text"] = f"Schulferien: {ferienname}"
        elif not status["in_schule"]:
            status["status_text"] = "Außerhalb der Schulzeit"
        
        return status

    @staticmethod
    def get_ferientage_vor() -> list:
        """Gibt die nächsten Schulferien zurück."""
        heute = date.today()
        kommende_ferien = []
        
        for ferien_name, ferien_data in SchulKontext.SCHULFERIEN_2025_2026.items():
            if ferien_data["start"] > heute:
                kommende_ferien.append(ferien_data)
        
        return sorted(kommende_ferien, key=lambda x: x["start"])[:1]

    @staticmethod
    def _get_wochentag_name(weekday: int) -> str:
        """Konvertiert Weekday zu deutschem Namen."""
        tage = ["Montag", "Dienstag", "Mittwoch", "Donnerstag", "Freitag", "Samstag", "Sonntag"]
        return tage[weekday]

    @staticmethod
    def _get_ferienname(datum: date) -> str:
        """Gibt den Namen der Ferien für ein bestimmtes Datum."""
        for ferien in SchulKontext.SCHULFERIEN_2025_2026.values():
            if ferien["start"] <= datum <= ferien["ende"]:
                return ferien["name"]
        return "Unbekannte Ferien"

    @staticmethod
    def get_schule_info() -> dict:
        """Gibt Informationen zur Schule zurück."""
        return {
            "name": "Glen Ames Senior Public School",
            "adresse": "Queen Street East, Toronto",
            "bezirk": "TDSB - Toronto District School Board",
            "kalender_link": "https://www.tdsb.on.ca/About-Us/School-Year-Calendar",
            "schulzeiten": {
                "start": "08:30",
                "ende": "15:30",
                "mittagspause": "12:10-13:00"
            }
        }
