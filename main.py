import streamlit as st
import os
from dotenv import load_dotenv
from audiorecorder import audiorecorder
import whisper

# --- SYSTEME ---
load_dotenv()

# --- SULEE IMPORTS ---
# Achte darauf, dass die Pfade zu deiner Ordnerstruktur passen!
from sulee.sulee_ki import SuleeKI
from sulee.interface.voice_engine import VoiceEngine
from sulee.persona.school_context import SchulKontext

# --- KONFIGURATION ---
st.set_page_config(page_title="Sulee Ardent", layout="wide")

# --- SIDEBAR: DER MONITOR ---
with st.sidebar:
    st.header("Sulees Status")
    
    # 1. Sulee initialisieren (nur einmal pro Session)
    if "sulee" not in st.session_state:
        with st.spinner("Sulee erwacht..."):
            st.session_state.sulee = SuleeKI()
            # Voice Engine laden
            try:
                st.session_state.voice = VoiceEngine()
            except Exception as e:
                st.warning(f"Stimme konnte nicht geladen werden: {e}")
                st.session_state.voice = None

    # 2. Bio-Daten anzeigen
    # Wir holen uns die Werte aus der neuen engine
    neuro = st.session_state.sulee.get_neuro_status()
    
    # Alter berechnen (formatiert)
    alter = neuro[3] / 3.4 # Rückrechnung aus deinem Dummy-Wert oder besser direkt aus Brain holen
    # Besser: Direkt aus Brain holen, falls du meine neue brain.py nutzt:
    try:
        bio_age = st.session_state.sulee.brain.get_age()
    except:
        bio_age = 13 # Fallback

    st.metric("Biologisches Alter", f"{bio_age} Jahre")
    
    # 3. Schul- & Zeitkontext (Die "Uhr")
    school = SchulKontext()
    status = school.get_aktueller_schulstatus()
    st.caption(f"Ort/Status: {status['status_text']}")
    
    st.divider()
    st.subheader("Einstellungen")
    debug_mode = st.checkbox("Debug Modus (Gedächtnis zeigen)")

# --- HAUPTBEREICH: CHAT ---
st.title("Sulee Ardent")
st.caption("Ein Gesprächspartner mit Gedächtnis und Stimme.")

# Chat History
if "messages" not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])
        if "audio" in message and message["audio"]:
            st.audio(message["audio"])

# --- INPUT SECTION ---

# 1. Audio Input (Mikrofon)
# Wir nutzen den Audiorecorder direkt als Input-Widget
st.subheader("Sprich mit Sulee")
audio = audiorecorder("Aufnahme starten", key="audio_rec")

if audio.duration_seconds > 0:
    audio_bytes = audio.export().read()
    st.audio(audio_bytes, format="audio/wav")
    
    # Whisper laden (falls nicht schon geschehen)
    if "whisper_model" not in st.session_state:
        with st.spinner("Ohren werden trainiert..."):
            st.session_state.whisper_model = whisper.load_model("base")

    with st.spinner("Sulee hört zu..."):
        # Speech to Text
        result = st.session_state.whisper_model.transcribe(audio_bytes, language="de")
        user_input = result["text"]
        
        if user_input and len(user_input) > 2:
            st.session_state["voice_input"] = user_input

# 2. Text Input (Tastatur)
# Prüfen, ob wir Audio-Input haben
if "voice_input" in st.session_state:
    prompt = st.session_state["voice_input"]
    del st.session_state["voice_input"]
else:
    prompt = st.chat_input("Oder tippe hier...")

# --- LOGIK LOOP ---
if prompt:
    # User Message anzeigen
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # Sulee Antwort generieren
    with st.spinner("Sulee denkt nach..."):
        # HIER RUFEN WIR DIE NEUE FUNKTION MIT STIMME AUF
        text_antwort, mood, audio_path = st.session_state.sulee.antwort_generieren(prompt, use_voice=True)
        
        # Antwort anzeigen
        st.session_state.messages.append({"role": "assistant", "content": text_antwort, "audio": audio_path})
        with st.chat_message("assistant"):
            st.markdown(text_antwort)
            if audio_path:
                st.audio(audio_path)
            
            if debug_mode:
                st.caption(f"System: {mood}")
