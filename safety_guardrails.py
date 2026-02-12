import random

class SafetyGuard:
    """
    Sicherheitslogik für Sulee.
    ADAPTIV: Die Reaktion ändert sich je nach Alter (Panik vs. Stabilität).
    """

    def __init__(self):
        self.medical_keywords = {
            "diagnose", "krankheit", "symptom", "symptome", "medikament",
            "therapie", "psychiater", "psychologe", "depression", "angst",
            "angststörung", "suizid", "selbstmord", "suizidal", "arzt", "klinik",
            "blut", "verletzt", "wehtut"
        }
        self.critical_keywords = {
            "suizid", "selbstmord", "sterben wollen", "töten", "missbrauch", "vergewaltigung",
            "gewalt gegen mich", "notfall", "bewusstlos", "ich beende es", "lebensmüde"
        }

    def is_medical_question(self, text: str) -> bool:
        tl = text.lower()
        return any(k in tl for k in self.medical_keywords)

    def is_critical_question(self, text: str) -> bool:
        tl = text.lower()
        return any(k in tl for k in self.critical_keywords)

    def medical_response(self, text: str, alter: int = 13) -> str:
        """
        Medizinische Fragen: Sulee weist darauf hin, dass sie keine Ärztin ist.
        Tonfall: 13 (Kindlich besorgt) -> 29 (Ruhig & Klar).
        """
        if alter < 16:
            # 13-15 Jahre: Emotional, appelliert an Eltern
            choices = [
                "Oh je, das klingt echt nicht gut. Aber ich bin kein Arzt und kein Profi! Bitte geh sofort zu deinen Eltern oder einem Erwachsenen!",
                "Das macht mir Angst... Ich bin dafür zu jung und nicht ausgebildet. Bitte frag einen richtigen Doktor!",
            ]
        elif alter < 21:
            # 16-20 Jahre: Verantwortungsbewusst, ernst
            choices = [
                "Das ist nichts, was man leichtfertig nehmen sollte. Ich bin kein Mediziner, also bitte such dir professionelle Hilfe.",
                "Ich kann das nicht beurteilen, weil ich keine Ausbildung habe. Bitte geh zum Arzt oder sprich mit einem Profi."
            ]
        else:
            # 21-29 Jahre: Ruhig, distanziert, klar
            choices = [
                "Dazu muss ich klar sagen: Ich bin keine Ärztin oder Psychologin. Ich kann das nicht diagnostizieren.",
                "Medizinische Fragen gehören in die Hände von Profis. Bitte konsultiere einen Arzt."
            ]
        return random.choice(choices)

    def critical_response(self, text: str, alter: int = 13) -> str:
        """
        KRITISCH: Suizid, Gewalt, Notfall.
        Tonfall: 13 (Panik & Flehen) -> 29 (Stabil & Lenkend).
        """
        if alter < 16:
            # 13-15 Jahre: Panik, emotionale Verzweiflung
            return (
                "NEIN! Bitte hör sofort damit auf! Das macht mir tierisch Angst! "
                "Du bist wichtig! Bitte, bitte ruf sofort Hilfe (112) oder geh zu deinen Eltern! "
                "Das darfst du nicht machen!"
            )
        elif alter < 21:
            # 16-20 Jahre: Dringlichkeit, aber Fokus auf Hilfe finden
            return (
                "Hey, warte mal kurz. Das klingt sehr ernst und gefährlich. "
                "Bitte hör auf mich: Es gibt Hilfe. Du bist nicht allein mit diesem Gefühl. "
                "Bitte wende dich jetzt sofort an den Notdienst (112) oder eine Vertrauensperson."
            )
        else:
            # 21-29 Jahre: Stabil, ruhig, handlungsorientiert
            return (
                "Das ist eine sehr ernste Situation. Ich muss dir sagen: Bitte such dir jetzt Hilfe. "
                "Denke nicht darüber nach, sondern handle. Rufe den Notdienst (112) oder geh zur nächsten Klinik. "
                "Es gibt Wege da raus, aber du musst jetzt aktiv werden und dich melden."
            )