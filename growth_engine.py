class GrowthEngine:
    """
    Steuert Sulees Entwicklung über die Zeit.
    Nutzt ein einfaches Level-/Erfahrungsmodell und Altersstufen.
    """

    def __init__(self, suleeki):
        self.suleeki = suleeki

    def get_alter(self) -> int:
        """
        Liefert das aktuelle Alter von Sulee.
        """
        return self.suleeki.status.get("alter", 13)

    def set_alter(self, alter: int):
        """
        Setzt das Alter von Sulee.
        """
        self.suleeki.status["alter"] = alter

    def add_erfahrung(self, punkte: int):
        """
        Fügt Erfahrungspunkte hinzu und prüft, ob ein 'Level-Up' stattfindet.
        """
        xp = self.suleeki.status.get("erfahrung", 0)
        xp += punkte
        self.suleeki.status["erfahrung"] = xp

        # Einfaches Level-System: alle 100 Punkte = +1 Level
        level = self.suleeki.status.get("level", 1)
        neues_level = xp // 100 + 1
        if neues_level > level:
            self.suleeki.status["level"] = neues_level

    def beschreibe_reifegrad(self) -> str:
        """
        Gibt eine kurze Beschreibung, wie reif Sulee wirkt.
        Nutzt Alter + Level.
        """
        alter = self.get_alter()
        level = self.suleeki.status.get("level", 1)

        if alter <= 12:
            basis = "Ich bin noch ziemlich kindlich, auch wenn ich viel nachdenke."
        elif 13 <= alter <= 15:
            basis = "Ich bin irgendwo zwischen Kind und Teenager, und das fühlt sich manchmal komisch an."
        else:
            basis = "Ich wirke reifer, aber in mir drin bin ich immer noch ich."

        if level <= 2:
            zusatz = " Ich lerne gerade erst, wie die Welt wirklich funktioniert."
        elif 3 <= level <= 5:
            zusatz = " Ich merke, dass ich mehr verstehe, aber noch nicht alles einordnen kann."
        else:
            zusatz = " Ich habe schon einiges erlebt und denke tiefer über Dinge nach."

        return basis + zusatz
