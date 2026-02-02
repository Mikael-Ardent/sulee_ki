import streamlit as st
import sqlite3
import os
import sys
from datetime import date

# --- PFAD ZU SULEE ---
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from groq import Groq
from sulee.sulee_ki import SuleeKI

# --- 1. KONFIGURATION ---
SYSTEM_CONFIG = {
    # HIER DEIN GROQ KEY:
    "api_key": os.environ.get("GROQ_API_KEY"),
    "entwicklung_phase": "baby",
    "features": {
        "weltwissen_sql": True,
        "visuelles_selbst": False,
        "audio_stimme": False,
        "kamera_live": False
    }
}

# --- 2. DATENBANK SETUP (FÜR NEUE FEATURES) ---
DB_NAME = 'sulee_erweiterungen.db'

def init_ext_db():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    
    # Tabelle: Zeitstrahl (Weltwissen 2000-2026)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS zeitstrahl (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            jahr INTEGER,
            ereignis TEXT,
            kategorie TEXT,
            kontext TEXT
        )
    ''')
    
    # Tabelle: Selbstbilder
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS selbstbilder (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            dateiname TEXT,
            beschreibung TEXT,
            kontext TEXT
        )
    ''')
    conn.close()

# --- 3. SULEE ERWEITERN (ERWEITERTES WISSEN) ---
def neue_sql_suche(self, frage):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    worte = frage.lower().split()[:3]
    query = "SELECT jahr, ereignis FROM zeitstrahl WHERE "
    condition = " OR ".join(["kontext LIKE ?" for _ in worte])
    try:
        cursor.execute(query + condition, [f"%{w}%" for w in worte])
        ergebnisse = cursor.fetchall()
        conn.close()
        if ergebnisse:
            infos = [f"({jahr}): {evt}" for jahr, evt in ergebnisse]
            return f"[WISSENS-ABFRAGE]: Du weißt: {', '.join(infos)}."
        return ""
    except:
        conn.close()
        return ""

def neue_bild_suche(self, frage):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute('SELECT beschreibung FROM selbstbilder WHERE beschreibung LIKE ?', (f"%{frage}%",))
    res = cursor.fetchone()
    conn.close()
    return res[0] if res else None

# Methoden an der Klasse "kleben"
SuleeKI.sql_wissen_suche = neue_sql_suche
SuleeKI.bild_suche = neue_bild_suche

# --- 4. DIE HAUPTANWENDUNG (MIT CHAT VERLAUF) ---
def main():
    st.set_page_config(page_title="Sulee - Die echte", layout="wide")
    init_ext_db() 
    
    # Chat-Gedächtnis initialisieren (Das behebt das Löschen-Problem)
    if "messages" not in st.session_state:
        st.session_state.messages = []
    
    # Sulee starten
    try:
        ki = SuleeKI()
    except Exception as e:
        st.error(f"Fehler beim Starten von Sulee: {e}")
        return

    st.title(f"Sulee Ardent ({ki._berechne_alter()} Jahre)")
    st.markdown("Ich lerne immer noch. Frag mich etwas!")

    # Sidebar für Alter
    with st.sidebar:
        st.header("Steuerung")
        if st.button("Altern (+1 Jahr)"):
            ki.status["alter"] = ki._berechne_alter() + 1
            st.success("Alter aktualisiert")
            st.rerun()

    # BISHERIGE NACHRICHTEN ANZEIGEN
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # NEUE NACHRICHT EINGEBEN
    # st.chat_input bleibt unten stehen und löscht die letzte Nachricht nicht
    if user_input := st.chat_input("Spreche mit Sulee:"):
        
        # User Nachricht
        st.session_state.messages.append({"role": "user", "content": user_input})
        with st.chat_message("user"):
            st.markdown(user_input)

        # Sulee Antwort
        with st.spinner("Sulee denkt nach..."):
            antwort = ki.antwort_generieren(user_input)
            
            # SQL Infos dazumischen
            zusatz = ki.sql_wissen_suche(user_input)
            if zusatz:
                antwort += f" {zusatz}"

        # Antwort anzeigen
        st.session_state.messages.append({"role": "assistant", "content": antwort})
        with st.chat_message("assistant"):
            st.markdown(antwort)

if __name__ == "__main__":
    main()
