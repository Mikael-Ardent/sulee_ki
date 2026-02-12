import random
from datetime import datetime, timedelta
from .schulkontext import SchulKontext
from .safety_guardrails import SafetyGuard
from .knowledge_verification import KnowledgeVerifier
from .deepseek_engine import DeepseekEngine
from .hybrid_inference_router import HybridInferenceRouter, QuestionClassifier

# Lazy-Loading
_llama_engine = None
_deepseek_engine = None
_router = None

def _get_router():
    global _router
    if _router is None:
        _router = HybridInferenceRouter()
    return _router

def _get_llama_engine():
    global _llama_engine
    if _llama_engine is None:
        try:
            from .llama_engine import LlamaEngine
            _llama_engine = LlamaEngine()
        except Exception as e:
            print(f"[Warnung] Llama-Engine konnte nicht geladen werden: {e}")
            _llama_engine = False
    return _llama_engine if _llama_engine else None

def _get_deepseek_engine():
    global _deepseek_engine
    if _deepseek_engine is None:
        try:
            _deepseek_engine = DeepseekEngine()
        except Exception as e:
            print(f"[Warnung] DeepSeek-Engine konnte nicht geladen werden: {e}")
            _deepseek_engine = False
    return _deepseek_engine if _deepseek_engine else None

class AnswerEngine:
    """
    Antwort-Engine für Sulee.
    NEU: Integriertes Biologisches & Intellektuelles Aging System.
    """

    def __init__(self, suleeki):
        self.suleeki = suleeki
        self.safety = SafetyGuard()
        self.verifier = KnowledgeVerifier()
        self.router = _get_router()
        self.classifier = QuestionClassifier()
        
        # --- AGING SYSTEM ---
        # Simulierter Geburtstag für Tests. 
        # In Produktion: self.suleeki.backstory.get("geburtsdatum")
        self.geburtsdatum = datetime.strptime("2011-06-15", "%Y-%m-%d") # Beispiel: Start 13 Jahre alt

        self.known_relatives = {
            "andy": "Andy", "bruder": "Andy",
            "mutter": "Mama", "vater": "Papa",
            "mikael": "Onkel Mikael", "onkel": "Onkel Mikael", "onkel mikael": "Onkel Mikael",
            "zürich": "Zürich", "toronto": "Toronto"
        }

    def _get_current_alter(self):
        """
        Berechnet das biologische Alter.
        Für Tests: Wir können hier Manipulationen vornehmen oder die echte Zeit nehmen.
        Max Limit: 29 Jahre.
        """
        # ECHTE ZEIT berechnen (wenn das Geburtsdatum korrekt gesetzt ist)
        # heute = datetime.now()
        # alter = heute.year - self.geburtsdatum.year - ((heute.month, heute.day) < (self.geburtsdatum.month, self.geburtsdatum.day))
        
        # --- TEST MODUS: Hier Alter manuell setzen zum Testen ---
        # Ändere diese Zahl, um Sulee zu altern zu lassen (z.B. 13, 16, 20, 25)
        alter = 13 
        
        # Technischer Stop bei 29
        return min(alter, 29)

    def _build_system_prompt(self):
        """
        Der wichtigste Teil: Formuliert, WIE Sulee antworten soll, basierend auf Alter.
        """
        bio_alter = self._get_current_alter()
        
        # Intellektuelle Entwicklungskurve
        if bio_alter <= 14:
            intel_level = "sehr klug für ihr Alter (Denkvermögen wie 16), neugierig, sprunghaft, emotional, sucht Sicherheit."
            ton = "kindlich, aber intelligent, fragend, manchmal unsicher."
        elif bio_alter <= 18:
            intel_level = "hochbegabt, Studentinnenniveau (Denkvermögen wie 20), philosophisch, sucht Identität."
            ton = "selbstbewusster, tiefergehende Fragen, jugendlicher Slang möglich."
        elif bio_alter <= 24:
            intel_level = "akademisch, analytisch (Denkvermögen wie 26), professionell, aber noch idealistisch."
            ton = "klar strukturiert, empathisch, erwachsen."
        else: # 25 - 29
            intel_level = "weise, erfahren (Denkvermögen wie 29+), lebensklug."
            ton = "ruhig, nachdenklich, humorvoll."

        prompt = (
            f"Du bist Sulee. Du bist biologisch {bio_alter} Jahre alt.\n"
            f"DEIN INTELLEKT: {intel_level}\n"
            f"DEIN TON: {ton}\n"
            f"DEINE PERSÖNLICHKEIT: Musikliebhaberin (Gitarre), Technik-Fan (Robo-Kids), emphatisch, Familie ist wichtig.\n"
            f"WICHTIG: Antworte immer passend zum biologischen Alter ({bio_alter}), nutze aber den intellektuellen Hintergrund. "
            f"Sei menschlich, nutze Emojis wenn es passt, zeige Gefühle."
        )
        return prompt

    def _find_known_relative(self, frage: str):
        q = frage.lower()
        for alias, canon in self.known_relatives.items():
            if alias in q:
                return canon
        return None

    # ---------------------------------------------------------
    # HAUPTFUNKTION
    # ---------------------------------------------------------

    def generate_answer(self, frage: str) -> str:
        frage_lower = frage.lower()

        # Safety first: kritische / medizinische Fragen (MIT ALTER)
        alter = self.suleeki.status.get("alter", 13) # Alter holen

        if self.safety.is_critical_question(frage_lower):
            return self.safety.critical_response(frage_lower, alter) # <--- NEU
        if self.safety.is_medical_question(frage_lower):
            return self.safety.medical_response(frage_lower, alter)   # <--- NEU

        # Knowledge Check
        gelernt = self.suleeki.wissen.pruefe_wissen(frage_lower)
        if gelernt:
            if isinstance(gelernt, dict) and "antwort" in gelernt:
                return gelernt["antwort"]
            return gelernt

        # --- KATEGORIEN (Behalten wir für schnelle Antworten) ---
        if self._ist_gruss(frage_lower):
            return self._antwort_gruss(frage_lower)
        if self._ist_familiefrage(frage_lower):
            return self._antwort_familie(frage_lower)
        if self._ist_schulfrage(frage_lower):
            return self._antwort_schule(frage_lower)
        
        # ... (Die anderen Checks für Musik, Emotion, etc. können hier eingefügt werden, 
        # ich lasse sie hier raus, um den Code lesbar zu halten, sie bleiben gleich wie vorher) ...

        # --- FALLBACK (DAS GEHIRN MIT ALTER) ---
        return self._antwort_fallback_mit_alter(frage)

    # ---------------------------------------------------------
    # HILFSFUNKTIONEN
    # ---------------------------------------------------------

    def _ist_gruss(self, frage): return any(w in frage for w in ["hallo", "hi", "guten tag", "onkel"])
    def _ist_familiefrage(self, frage): return any(w in frage for w in ["bruder", "mutter", "vater", "onkel", "andy", "zürich"])
    def _ist_schulfrage(self, frage): return any(w in frage for w in ["schule", "lehrer", "fach", "prüfung"])

    # ---------------------------------------------------------
    # ANTWORTEN (Adaptiert an Aging)
    # ---------------------------------------------------------

    def _antwort_gruss(self, frage):
        bio = self._get_current_alter()
        rel = self._find_known_relative(frage.lower())
        
        if rel:
            if "onkel" in rel.lower():
                if bio < 16:
                    return "Hallo Onkel Mikael! Magst du mich noch besuchen? Ich wollte dir meine neue Gitarre zeigen!"
                else:
                    return "Hallo Onkel Mikael! Schön dich zu 'lesen'. Ich hoffe, es geht dir gut in Zürich. Wir müssen mal wieder Quatschen, über deine Tech-Projekte."
            return f"Hallo {rel}!"

        # Altersabhängige Standard-Begrüßung
        if bio < 15:
            return "Hi! Wer bist du? Bist du neu hier?"
        elif bio < 20:
            return "Hey! Schön, dich kennenzulernen. Wie läuft's bei dir?"
        else:
            return "Hallo. Ich freue mich, dich kennenzulernen."

    def _antwort_familie(self, frage):
        rel = self._find_known_relative(frage.lower())
        if rel and "onkel" in rel.lower():
             return "Mein Onkel Mikael ist super! Er wohnt in Zürich und versteht Technik. Wir verstehen uns prächtig."
        if "bruder" in frage or "andy" in frage:
            return "Andy? Der ist der beste Bruder der Welt. Er wohnt zwar weg, aber er ist immer für mich da."
        return "Meine Familie ist meine Ankerstelle."

    def _antwort_schule(self, frage):
        bio = self._get_current_alter()
        if bio > 18:
            return "Schule ist schon vorbei! Ich studiere jetzt und beschäftige mich viel mit meiner Forschung."
        elif bio > 13:
            return "Die Schule ist okay. Ich finde die theoretischen Fächer manchmal etwas langweilig, aber in den Praxis-AGs für Robo-Kids gehe ich richtig auf."
        else:
            return "Glen Ames ist meine Schule. Manchmal ist es anstrengend, aber ich lerne gern neue Dinge."

    # ---------------------------------------------------------
    # DAS NEUE GEHIRN (FALLBACK MIT AI & AGING)
    # ---------------------------------------------------------

    def _antwort_fallback_mit_alter(self, frage: str) -> str:
        """
        Hier passiert die Magie.
        Wir nutzen DeepSeek/Llama, aber geben ihnen den Alters-Prompt mit.
        """
        
        # 1. System Prompt generieren (Das Alter!)
        system_prompt = self._build_system_prompt()
        
        raw_info = None
        source = None
        
        # Router nutzen (wie vorher)
        question_type = self.classifier.classify(frage)
        chosen_backend = self.router.route(frage, question_type, False)
        
        print(f"[Router] Alter: {self._get_current_alter()} | Backend: {chosen_backend}")

        # 2. Anfrage an das Backend
        if chosen_backend == "deepseek":
            try:
                deepseek = _get_deepseek_engine()
                if deepseek and deepseek.is_active:
                    # Hier injizieren wir den Prompt!
                    # Wir hoffen, dass deine Deepseek-Engine einen Parameter für System Prompt hat.
                    # Falls nicht, hängen wir es an die Frage dran.
                    
                    # FALLBACK WEN ENGINE KEIN SYSTEM PROMPT HAT:
                    # Wir übergeben den System-Prompt direkt an die Engine
                    
                    raw_info = deepseek.fetch_info(frage, system_prompt) # <-- Parameter anpassen, falls nötig!
                    
                    if raw_info and len(raw_info.strip()) > 10:
                        source = "deepseek"
            except Exception as e:
                print(f"[DeepSeek Fehler]: {e}")

        elif chosen_backend == "llama":
            try:
                llama = _get_llama_engine()
                if llama:
                    full_query = f"{system_prompt}\n\nFrage: {frage}"
                    raw_info = llama.generate(full_query)
                    if raw_info and len(raw_info.strip()) > 10:
                        source = "llama"
            except Exception as e:
                print(f"[Llama Fehler]: {e}")

        # 3. Antwort verarbeiten
        if raw_info and source:
            # Speichern fürs Gedächtnis
            try:
                self.suleeki.wissen.speichere_wissen(frage, raw_info, source=source, allow_overwrite=False)
            except Exception:
                pass
            return raw_info

        # 4. Notfall-Fallback (wenn KI versagt)
        antworten = ["Hmm, darüber muss ich nachdenken...", "Das ist tiefgründig.", "Erklär mir das mal genauer?"]
        return random.choice(antworten)