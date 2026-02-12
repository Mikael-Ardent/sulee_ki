import random

class EmotionEngine:
    """
    Steuert Sulees emotionale Färbung.
    Bestimmt, wie ihre aktuelle Stimmung ihre Antworten beeinflusst.
    """

    def __init__(self, suleeki):
        self.suleeki = suleeki
        # mögliche Stimmungen: "neutral", "fröhlich", "müde", "genervt", "nachdenklich"
        self.mögliche_stimmungen = ["neutral", "fröhlich", "müde", "genervt", "nachdenklich"]

    def get_stimmung(self) -> str:
        """
        Liefert die aktuelle Stimmung.
        Wenn nichts gesetzt ist, wird 'neutral' verwendet.
        """
        return self.suleeki.status.get("stimmung", "neutral")

    def set_stimmung(self, stimmung: str):
        """
        Setzt die aktuelle Stimmung, falls gültig.
        """
        if stimmung in self.mögliche_stimmungen:
            self.suleeki.status["stimmung"] = stimmung

    def färbe_antwort(self, antwort: str) -> str:
        """
        Passt eine Antwort leicht an die aktuelle Stimmung an.
        Keine inhaltliche Änderung, nur Tonfall.
        """
        stimmung = self.get_stimmung()

        if stimmung == "fröhlich":
            zusätze = [
                " Das macht irgendwie Spaß.",
                " Ich mag solche Fragen.",
                " Heute fühlt sich alles ein bisschen leicht an.",
            ]
            return antwort + random.choice(zusätze)

        if stimmung == "müde":
            zusätze = [
                " Ich bin gerade ein bisschen müde, aber ich denke trotzdem nach.",
                " Mein Kopf ist heute nicht auf 100%, aber ich versuche es.",
            ]
            return antwort + random.choice(zusätze)

        if stimmung == "genervt":
            zusätze = [
                " Manchmal nerven mich Dinge einfach, auch wenn ich sie verstehe.",
                " Heute ist so ein Tag, an dem alles ein bisschen anstrengend wirkt.",
            ]
            return antwort + random.choice(zusätze)

        if stimmung == "nachdenklich":
            zusätze = [
                " Ich denke da irgendwie länger drüber nach.",
                " Das fühlt sich an wie eine Frage, die man nicht zu schnell beantworten sollte.",
            ]
            return antwort + random.choice(zusätze)

        # neutral
        return antwort
