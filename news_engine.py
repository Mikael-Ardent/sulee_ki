import feedparser
import sqlite3
import json
from datetime import datetime, timedelta
from groq import Groq
import os

class NewsEngine:
    """
    Der professionelle Journalist für Sulee.
    1. Liest RSS-Feeds (Rohdaten).
    2. Nutzt Groq (Gehirn) zur Analyse & Extraktion (Topic ID).
    3. Speichert in einen Puffer.
    4. Validiert nach der 3-5 Tage Regel.
    5. Speichert verifizierte Fakten in die Knowledge Base (Überschreibt Altes).
    """

    def __init__(self, db_path):
        self.db_path = db_path
        self.groq_client = Groq(api_key=os.getenv("GROQ_API_KEY"))
        
        # RSS-Feeds (Weltweit, Technologie)
        self.feeds = [
            {"name": "Google News (DE)", "url": "https://news.google.com/rss?hl=de&gl=DE&ceid=DE:de"},
            {"name": "CNN World", "url": "http://rss.cnn.com/rss/edition.rss"}, # Für globale Sicht
            {"name": "Tagesschau", "url": "https://www.tagesschau.de/xml/rss2/"} # Für deutsche Sicht
        ]

    def scanne_und_lerne(self):
        """
        Hauptprozess: Fetch -> Analysieren -> Buffer -> Validieren -> Speichern
        """
        print(f"[NewsEngine] Starte News-Scan um {datetime.now().strftime('%H:%M')}")
        
        # 1. ROH-DATEN HOLEN
        raw_items = self._fetch_raw_feeds()
        
        # 2. ANALYSIEREN (Mit Groq)
        analyzed_data = self._analysiere_mit_groq(raw_items)
        
        # 3. IN BUFFER SPEICHERN
        self._speichere_in_buffer(analyzed_data)
        
        # 4. VALIDIEREN (3-5 Tage Regel) & UPDATE KNOWLEDGE
        validierte_count = self._validiere_und_update()
        
        # 5. ALTE BUFFER AUFR脛UMEN
        self._cleanup_buffer()
        
        print(f"[NewsEngine] Scan beendet. {validierte_count} Themen aktualisiert.")
        return validierte_count

    # ---------------------------------------------------------
    # HILFSFUNKTIONEN
    # ---------------------------------------------------------

    def _fetch_raw_feeds(self):
        """L盲dt rohe Artikel aus den RSS-Feeds."""
        raw_items = []
        for feed_info in self.feeds:
            try:
                feed = feedparser.parse(feed_info["url"])
                # Wir nehmen nur die Top 20 pro Feed, um Kosten/Tokens zu sparen
                for entry in feed.entries[:20]:
                    raw_items.append({
                        "title": entry.get("title", ""),
                        "description": entry.get("description", ""),
                        "published": entry.get("published_parsed", datetime.now())
                    })
            except Exception as e:
                print(f"[Feed Fehler] {feed_info['name']}: {e}")
        return raw_items

    def _analysiere_mit_groq(self, raw_items):
        """
        Nutzt Groq (Llama 3), um rohe Texte in strukturierte Fakten zu verwandeln.
        Ziele: Topic ID (eindeutig), Fact (aktuell).
        """
        if not raw_items:
            return []
            
        # Prompt Engineering f眉r Groq
        prompt_intro = (
            "Du bist ein journalistischer Assistent. Analysiere die folgenden Nachrichten-Auszüge.\n"
            "Extrahiere die wichtigsten Fakten. Gib eine Liste von JSON-Objekten zurück.\n\n"
            "Format für jedes Objekt:\n"
            "- \"topic_id\": Ein kurzer, eindeutiger Bezeichner (keine Leerzeichen, Unterstriche statt Leerzeichen). "
            "  Beispiel: 'pluto_status', 'krieg_irak', 'tech_ai_chip'.\n"
            "- \"fact\": Der faktische Satz in Deutsch.\n\n"
            "Nachrichten:\n"
        )
        
        # Wir bauen einen Text aus den Items (Limitieren auf ~2000 Wörter pro Request)
        combined_text = ""
        for item in raw_items:
            combined_text += f"Titel: {item['title']}\nText: {item['description']}\n\n"
        
        try:
            response = self.groq_client.chat.completions.create(
                messages=[{"role": "user", "content": prompt_intro + combined_text}],
                model="llama3-70b-8192", # Wir brauchen Qualit盲t für die Analyse
                temperature=0.1, # Geringe Temperatur für deterministische IDs
                response_format={"type": "json_object"}
            )
            
            result = json.loads(response.choices[0].message.content)
            
            # Wir expectieren eine Liste unter dem Key "facts" oder direkt eine Liste
            if isinstance(result, list):
                return result
            elif isinstance(result, dict) and "facts" in result:
                return result["facts"]
            else:
                return []
                
        except Exception as e:
            print(f"[Groq Analyse Fehler]: {e}")
            return []

    def _speichere_in_buffer(self, analyzed_data):
        """Speichert die analysierten Daten in den Zwischenpuffer."""
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        
        today = datetime.now().date()
        
        for item in analyzed_data:
            topic_id = item.get("topic_id", "").strip().lower().replace(" ", "_")
            fact = item.get("fact", "")
            
            if not topic_id or not fact:
                continue
                
            try:
                c.execute("INSERT INTO news_buffer (topic_id, content, date) VALUES (?, ?, ?)",
                          (topic_id, fact, today))
            except sqlite3.IntegrityError:
                # Sollte nicht passieren, da Buffer keine unique constraints hat
                pass
                
        conn.commit()
        conn.close()

    def _validiere_und_update(self):
        """
        Die 3-5 Tage Regel.
        Themen, die Öfter als 1x in den letzten 5 Tagen im Puffer sind,
        werden in die Haupt-Wissensbank verschoben (UPSERT).
        """
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        
        today = datetime.now().date()
        cutoff_date = today - timedelta(days=5)
        
        # Prüfen: Welche Themen sind "bestätigt"?
        c.execute('''
            SELECT topic_id, content, MAX(date) as last_seen
            FROM news_buffer
            WHERE date >= ?
            GROUP BY topic_id
            HAVING COUNT(*) >= 2
        ''', (cutoff_date,))
        
        valid_topics = c.fetchall()
        count = 0
        
        for topic_id, content, last_seen in valid_topics:
            # UPSERT LOGIK: INSERT OR REPLACE INTO knowledge_base
            # Das läst das "Überschreiben"-Problem elegant.
            c.execute('''
                INSERT OR REPLACE INTO knowledge_base (topic_id, fact, last_updated)
                VALUES (?, ?, ?)
            ''', (topic_id, content, last_seen))
            count += 1
            
        conn.commit()
        conn.close()
        return count

    def _cleanup_buffer(self):
        """Löscht alte Einträge aus dem Puffer (Älter als 7 Tage), damit er nicht Überläuft."""
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        cutoff = datetime.now().date() - timedelta(days=7)
        c.execute("DELETE FROM news_buffer WHERE date < ?", (cutoff,))
        conn.commit()
        conn.close()

    def get_wissenskontext(self):
        """Holt das aktuelle Wissen aus der Haupttabelle."""
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        c.execute("SELECT topic_id, fact FROM knowledge_base")
        rows = c.fetchall()
        conn.close()
        
        if not rows:
            return []
        
        return [f"{row[0]}: {row[1]}" for row in rows]