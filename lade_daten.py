import sqlite3
import os
from groq import Groq
from dotenv import load_dotenv # Falls du .env nutzt, sonst os.environ

# --- 1. KONFIGURATION ---
DB_NAME = 'sulee_lebenslauf.db'
BILDER_ORDNER = 'assets/images/sulee' # Ordner erstellen, wo die Fotos liegen

# Wir nutzen Groq, da es im Free-Tier am stabilsten ist
# Wenn du Deepseek nutzen willst, müsstest du hier den Client tauschen
client = Groq(api_key=os.environ.get("GROQ_API_KEY"))

# --- 2. WELTWISSEN DATEN (2000 - 2026) ---
# Hier ist die Liste strukturiert. Du kannst den Rest hier unten weiter schreiben.
weltwissen_daten = [
    {
        "jahr": 2000,
        "ereignis": "Platzen der Dotcom-Blase",
        "kategorie": "Wirtschaft/Tech",
        "kontext": "Spekulationsboom an den Aktienmärkten (insb. Internetfirmen) endet in einer Rezession."
    },
    {
        "jahr": 2001,
        "ereignis": "Anschläge vom 11. September",
        "kategorie": "Politik/Terror",
        "kontext": "Terroranschläge auf das World Trade Center in New York und das Pentagon. Beginn des 'Krieg gegen Terror'."
    },
    {
        "jahr": 2003,
        "ereignis": "Irakkrieg",
        "kategorie": "Krieg",
        "kontext": "USA und Verbündete marschieren im Irak ein. Beginn eines langjährigen Konflikts."
    },
    {
        "jahr": 2004,
        "ereignis": "Tsunami im Indischen Ozean",
        "kategorie": "Natur",
        "kontext": "Ein gewaltiges Seebeben löst eine Flutwelle aus, über 230.000 Menschen sterben."
    },
    {
        "jahr": 2008,
        "ereignis": "Finanzkrise & Obama Wahl",
        "kategorie": "Wirtschaft/Politik",
        "kontext": "Zusammenbruch der Lehman Brothers löst globale Wirtschaftskrise aus. Barack Obama wird erster schwarzer US-Präsident."
    },
    {
        "jahr": 2011,
        "ereignis": "Fukushima Katastrophe",
        "kategorie": "Natur/Tech",
        "kontext": "Erdbeben und Tsunami verursachen Super-GAU in Japans Atomkraftwerk. Globale Debatte über Atomkraft."
    },
    {
        "jahr": 2016,
        "ereignis": "Brexit & Trump Wahl",
        "kategorie": "Politik",
        "kontext": "UK stimmt für EU-Austritt. Donald Trump wird US-Präsident (America First)."
    },
    {
        "jahr": 2019,
        "ereignis": "Beginn COVID-19",
        "kategorie": "Gesundheit",
        "kontext": "Ausbruch des Coronavirus in Wuhan, China."
    },
    {
        "jahr": 2020,
        "ereignis": "Pandemie & Lockdown",
        "kategorie": "Gesellschaft",
        "kontext": "COVID-19 verbreitet sich global. Lockdowns lähmen Wirtschaft und Leben."
    },
    {
        "jahr": 2022,
        "ereignis": "Ukraine Krieg",
        "kategorie": "Krieg",
        "kontext": "Russland greift die Ukraine völkerrechtswidrig an. Energiekrise und Inflation in Europa."
    },
    {
        "jahr": 2023,
        "ereignis": "KI-Boom (ChatGPT)",
        "kategorie": "Tech",
        "kontext": "KI dringt massiv durch Tools wie ChatGPT in den Alltag ein."
    }
    # FÜGE HIER WEITERE JAHRE BIS 2026 HINZU...
]

# --- 3. FUNKTIONEN ---

def init_db_check():
    """Prüft ob DB existiert, falls nicht Fehlermeldung."""
    if not os.path.exists(DB_NAME):
        print(f"FEHLER: Datenbank '{DB_NAME}' nicht gefunden!")
        print(f"Bitte starte zuerst 'main.py', damit die Datenbank erstellt wird.")
        return False
    return True

def import_weltwissen():
    """Fügt das Weltwissen in die SQL Datenbank ein."""
    if not init_db_check(): return

    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    
    inserted = 0
    for item in weltwissen_daten:
        # Prüfen ob Eintrag schon existiert (am Ereignis)
        cursor.execute('SELECT id FROM zeitstrahl WHERE ereignis = ?', (item['ereignis'],))
        if cursor.fetchone() is None:
            cursor.execute('''
                INSERT INTO zeitstrahl (jahr, ereignis, kategorie, kontext)
                VALUES (?, ?, ?, ?)
            ''', (item['jahr'], item['ereignis'], item['kategorie'], item['kontext']))
            inserted += 1
            print(f"+ Eingefügt: {item['jahr']} - {item['ereignis']}")
        else:
            print(f"- Übersprungen (existiert): {item['jahr']} - {item['ereignis']}")
    
    conn.commit()
    conn.close()
    print(f"\nFertig! {inserted} neue Einträge im Weltwissen.")

def import_bilder():
    """Analysiert Bilder mit Groq Vision und speichert Erkenntnisse."""
    if not init_db_check(): return
    
    if not os.path.exists(BILDER_ORDNER):
        print(f"INFO: Ordner '{BILDER_ORDNER}' existiert noch nicht oder ist leer.")
        print(f"Lege Ordner an und stecke Fotos hinein, falls du willst.")
        return

    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    
    dateien = os.listdir(BILDER_ORDNER)
    counter = 0
    
    print(f"\nStarte Bildanalyse... (Geduld, das dauert pro Bild ein paar Sekunden)")
    
    for datei in dateien:
        if datei.lower().endswith(('.png', '.jpg', '.jpeg', '.webp')):
            pfad = os.path.join(BILDER_ORDNER, datei)
            
            # Prüfen ob schon analysiert
            cursor.execute('SELECT id FROM selbstbilder WHERE dateiname = ?', (datei,))
            if cursor.fetchone():
                print(f"- Übersprungen (bereits analysiert): {datei}")
                continue
                
            print(f"Analysiere: {datei}...")
            
            try:
                # Groq Vision Prompt
                completion = client.chat.completions.create(
                    model="llama-3.2-11b-vision-preview",
                    messages=[
                        {
                            "role": "user",
                            "content": [
                                {"type": "text", "text": "Beschreibe dieses Bild extrem kurz für ein Gedächtnis. Nutze dieses Format exakt: 'Alter: [ca. Jahre]. Kleidung: [Beschreibung]. Aktivität: [Was tut sie?]. Stimmung: [Stimmung].'"},
                                {"type": "image_url", "image_url": {"url": f"file://{pfad}"}},
                            ],
                        }
                    ],
                    temperature=0.1
                )
                
                beschreibung = completion.choices[0].message.content
                
                cursor.execute('''
                    INSERT INTO selbstbilder (dateiname, beschreibung, kontext)
                    VALUES (?, ?, ?)
                ''', (datei, beschreibung, "eigenes foto"))
                
                conn.commit()
                print(f"-> Gespeichert: {beschreibung[:60]}...")
                counter += 1
                
            except Exception as e:
                print(f"-> FEHLER bei {datei}: {e}")

    conn.close()
    print(f"\nBildanalyse abgeschlossen. {counter} neue Bilder gespeichert.")

# --- 4. MAIN START ---
if __name__ == "__main__":
    print("=== SULEE DATA UPLOADER ===")
    print("1. Weltwissen (2000-2026) importieren? (j/n)")
    # Für automatischen Ablauf im Codespace kannst du auch direkt die Funktionen aufrufen:
    
    import_weltwissen()
    
    print("\n2. Selbstbilder analysieren? (Nur wenn Bilder im Ordner sind)")
    import_bilder()