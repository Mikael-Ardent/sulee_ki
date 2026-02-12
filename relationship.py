# sulee/core/relationship.py

class RelationshipManager:
    """
    Verwaltet, wie Sulee User einschätzt.
    Von "Fremder" über "Bekannten" bis "Freund" basierend auf Verhalten (Respekt, Anstand).
    """

    def __init__(self):
        # user_id hier vereinfacht als Key (z.B. Name)
        self.beziehungen = {}
        
    def update_interaktion(self, user_name: str, ist_höflich: bool):
        if user_name not in self.beziehungen:
            # Neuer User startet bei 0 (Neutral)
            self.beziehungen[user_name] = 0
            
        if ist_höflich:
            # Höflichkeit erhöht den Score (+1)
            self.beziehungen[user_name] += 1
        else:
            # Unhöflichkeit senkt ihn (-2, "Vertrauensverlust")
            self.beziehungen[user_name] -= 2

    def get_status(self, user_name: str) -> str:
        score = self.beziehungen.get(user_name, 0)
        
        if score < -5:
            return "feindselig" # Sehr unhöflich gewesen
        elif score < 5:
            return "fremd"      # Neutral
        elif score < 15:
            return "bekannt"    # Ein paar Mal nett geredet
        else:
            return "freund"     # Langfristig sehr respektvoll