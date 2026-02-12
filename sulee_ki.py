import os
import random
import streamlit as st
from groq import Groq

# Interne Importe aus deiner Struktur
from sulee.brain import SuleeBrain
from sulee.config import BACKSTORY_CORE, AGING_FACTOR, START_AGE
from sulee.emotion_engine import EmotionEngine

class SuleeKI:
    def __init__(self):
        # --- 1. API KEY MANAGEMENT (Streamlit First) ---
        # Versucht zuerst den Key aus den Streamlit Secrets zu holen (Cloud)
        # Fallback auf lokale .env Datei (Lokale Entwicklung)
        api_key = st.secrets.get("GROQ_API_KEY")
        if not api_key:
            api_key = os.getenv("GROQ_API_KEY")
        
        if not api_key:
            raise ValueError("FEHLER: Kein GROQ_API_KEY gefunden! Bitte Streamlit Secrets oder .env prüfen.")

        # Client starten
        self.client = Groq(api_key=api_key)
        
        # --- 2. SUB-SYSTEME INITIALISIEREN ---
        # Das Gehirn (Bio-Clock, Gedächtnis, Backstory)
        self.brain = SuleeBrain()
        
        # Die Neuro-Chemie (Stimmungen, Gefühle)
        self.emotion = EmotionEngine()
        
        # Das Sprachmodell
        self.model = "llama3-70b-8192" 

        # Voice Engine (Lazy Loading: Wir laden sie erst, wenn wir sie brauchen,
        # um Startzeit zu sparen und Fehler zu vermeiden, wenn Dateien fehlen)
        self.voice = None

    def _init_voice_if_needed(self):
        """Lädt die VoiceEngine nur beim ersten Bedarf."""
        if self.voice is None:
            try:
                from sulee.interface.voice_engine import VoiceEngine
                self.voice = VoiceEngine()
                print("[SuleeKI] VoiceEngine erfolgreich geladen.")
            except Exception as e:
                print(f"[SuleeKI] Warnung: VoiceEngine konnte nicht geladen werden: {e}")
                self.voice = False # Markieren als gescheitert, damit wir es nicht nochmal versuchen

    def _get_mood(self):
        """Bestimmt eine Basis-Stimmung (kann später durch Neuro erweitert werden)."""
        moods = ["neutral", "neugierig", "zickig", "übermüdet", "euphorisch", "nachdenklich"]
        return random.choice(moods)

    def _get_age_style(self, age):
        """Gibt Verhaltensweisen basierend auf dem Alter zurück."""
        if age < 15:
            return (
                "Du bist ein Teenager (13-15). Du nutzt manchmal Jugendsprache. "
                "Du reagierst impulsiv. Du willst erwachsen wirken, bist es aber noch nicht. "
                "Du kannst 'krass' oder 'boah' sagen. Du fragst oft nach dem 'Warum'."
            )
        elif age < 20:
            return (
                "Du bist ein junger Erwachsener (16-20). Du.beginnst ernster zu werden. "
                "Dein Wortschatz wird präziser. Du interessierst dich stark für Wissenschaft und Logik. "
                "Du entwickelst deine eigenen Meinungen und verteidigst sie."
            )
        else:
            return (
                "Du bist eine junge Frau (21-29). Du bist intelligent, analytisch und professionell. "
                "Du sprichst klar, aber nicht ohne Gefühl. Du hast Humor. "
                "Du bist auf dem Weg, eine Expertin für KI zu werden."
            )

    def antwort_generieren(self, user_input, use_voice=False):
        """
        Hauptfunktion zur Generierung einer Antwort.
        """
        
        # --- 1. BIOLOGISCHES STATUS ---
        # Alter aus der Bio-Clock holen
        age = self.brain.get_age()
        
        # Neuro-Werte simulieren (Dopamin, Serotonin, Kortisol, Energie)
        # In einer fortgeschrittenen Version würden diese aus der DB oder einem State geladen
        neuro_vals = (random.randint(40, 80), random.randint(40, 80), random.randint(20, 50), random.randint(50, 90))
        
        # Emotionale Analyse anhand der Neuro-Werte
        emotion_instruction = self.emotion.analyse_neuro_status(neuro_vals)
        mood_tag = self.emotion.get_audio_emotion_tag(neuro_vals)
        
        # --- 2. KONTEXT & GEDÄCHTNIS ---
        # Textuelle Erinnerungen
        memories = self.brain.get_relevant_memories(user_input)
        memory_text = "\n".join([f"[Erinnerung]: {m[0]}" for m in memories])
        
        # Visuelle Erinnerungen (Fotos), wenn nach Aussehen gefragt wird
        visual_text = ""
        if any(w in user_input.lower() for w in ["aussehen", "foto", "bild", "siehst", "kleidung", "haar"]):
            vis_mems = self.brain.recall_visual_memory(age)
            if vis_mems:
                visual_text = "\n".join([f"[VISUELLES GEDÄCHTNIS]: {mem}" for mem in vis_mems])

        # Backstory Details (Familie, Wohnort) aus dem Brain holen
        backstory_details = self.brain.get_backstory_context()
        
        # --- 3. SYSTEM PROMPT BAUEN (DAS HERZ) ---
        system_prompt = f"""
        {BACKSTORY_CORE.format(age=age)}
        
        {backstory_details}
        
        AKTUELLER STATUS:
        - Alter: {age} Jahre.
        - Neuro-Zustand: {emotion_instruction}
        - Gefühl: {mood_tag}
        
        ERINNERUNGEN (Kontext):
        {memory_text if memory_text else "Keine passenden Erinnerungen."}
        
        VISUELLE ERINNERUNG:
        {visual_text if visual_text else "Keine passenden Fotos im Gedächtnis."}
        
        ANWEISUNG:
        - Bleibe absolut im Charakter von Sulee ({age} Jahre).
        - Nutze die Infos aus IDENTITÄT & FAMILIE.
        - Reagiere auf deinen Neuro-Zustand ({mood_tag}).
        - Wenn du zickig bist, sei kurz und sarkastisch.
        - Wenn du euphorisch bist, nutze Ausrufezeichen.
        """

        # --- 4. API CALL (GROQ / LLAMA) ---
        text_antwort = ""
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_input}
                ],
                temperature=0.8,
                max_tokens=1024
            )
            text_antwort = response.choices[0].message.content
            
        except Exception as e:
            text_antwort = f"Sorry, ich hatte einen Blackout... (Fehler: {str(e)})"
            mood_tag = "confused"

        # --- 5. SPEICHERN (LERNEN) ---
        # Wir speichern die Interaktion im Langzeitgedächtnis
        self.brain.save_memory(user_input, mood_tag, importance=3)

        # --- 6. AUDIO GENERIERUNG (Falls gewünscht) ---
        audio_path = None
        if use_voice:
            self._init_voice_if_needed()
            if self.voice: # Prüfen ob erfolgreich geladen
                try:
                    # Generiere Audio basierend auf der Emotion (mood_tag)
                    audio_path = self.voice.generiere_audio(text_antwort, emotion=mood_tag)
                except Exception as e:
                    print(f"[Audio Fehler] {e}")
                    # Fallback: Wir geben den Text zurück, auch wenn Audio fehlschlägt
                    pass

        return text_antwort, mood_tag, audio_path

    def get_neuro_status(self):
        """
        Gibt einen Tuple zurück für die Sidebar in main.py.
        Format: (Dopamin, Serotonin, Kortisol, Energie/Alter_dummy)
        """
        # Wir geben hier simulierte Werte zurück, da wir keinen dauerhaften State haben.
        # Das Alter holen wir aber echt.
        age = self.brain.get_age()
        return (50, 50, 50, int(age)) # Letzter Wert wird in Sidebar als "Energie/Alter" genutzt
