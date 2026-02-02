import streamlit as st
import sqlite3
import os
import sys

# --- 1. PFAD ZU SULEE ---
# Damit Python den Ordner 'sulee' findet
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from groq import Groq
from sulee.sulee_ki import SuleeKI

# --- 2. DATENBANK SETUP (Für die neuen Features) ---
# Wir erstellen die SQL-DB extra neben der JSON-Datei
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

# --- 3. SULEE ERWEITERN (Monkey Patching) ---
# Wir fügen deiner SuleeKI-Klasse die neuen Methoden für SQL hinzu,
# ohne deine Datei `sulee_ki.py` neu schreiben zu müssen (weniger Fehler!).

def neue_sql_suche(self, frage):
    """Sucht nach Weltwissen in SQL."""
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
    """Sucht nach Bildern."""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute('SELECT beschreibung FROM selbstbilder WHERE beschreibung LIKE ?', (f"%{frage}%",))
    res = cursor.fetchone()
    conn.close()
    return res[0] if res else None

# Die Methoden an die Klasse "kleben"
SuleeKI.sql_wissen_suche = neue_sql_suche
SuleeKI.bild_suche = neue_bild_suche

# --- 4. UI (Frontend) ---

def main():
    st.set_page_config(page_title="Sulee - Die echte", layout="wide")
    init_ext_db() # DB einmal checken
    
    # Sulee initialisieren
    # ACHTUNG: Hier muss dein Groq Key rein, falls du ihn nicht in .env hast
    # Deine sulee_ki.py braucht den Key wahrscheinlich auch oder wir übergeben ihn hier.
    # Für den Moment nutzen wir die Env-Variable wie gehabt.
    
    try:
        ki = SuleeKI() # Initialisiert deine große Klasse
    except Exception as e:
        st.error(f"Fehler beim Starten von Sulee: {e}")
        st.write("Tipp: Prüfe den API Key in 'sulee/sulee_ki.py' oder hier in main.py")
        return

    st.title(f"Sulee Ardent ({ki._berechne_alter()} Jahre)")
    st.markdown("Ich lerne immer noch. Frag mich etwas!")

    # Sidebar für Alter
    with st.sidebar:
        st.header("Steuerung")
        if st.button("Altern (+1 Jahr)"):
            # Wir nutzen deine interne Logik
            ki.status["alter"] = ki._berechne_alter() + 1
            st.success("Alter aktualisiert")
            st.rerun()

    # Chat
    user_input = st.text_input("Spreche mit Sulee:")
    
    if st.button("Senden"):
        if user_input:
            # 1. Antwort aus deinem System
            antwort = ki.antwort_generieren(user_input)
            
            # 2. Neue SQL-Infos dazu holen (wenn vorhanden)
            zusatz = ki.sql_wissen_suche(user_input)
            if zusatz:
                antwort += f" {zusatz}" # Infos dranhängen
            
            st.chat_message("user").write(user_input)
            st.chat_message("assistant").write(antwort)

if __name__ == "__main__":
    main()