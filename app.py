from flask import Flask, request, jsonify, render_template
from sulee.sulee_ki import SuleeKI
import os

app = Flask(__name__, template_folder='templates')
sulee = SuleeKI()

# ---------------------------------------------------------
# WEB ROUTES
# ---------------------------------------------------------

@app.route("/")
def index():
    """Serviert das Chat Frontend"""
    return render_template("index.html")


# ---------------------------------------------------------
# API ROUTES
# ---------------------------------------------------------

@app.route("/api/chat", methods=["POST"])
def chat():
    """Chat Endpoint - generiert eine Antwort von Sulee"""
    try:
        data = request.get_json()
        frage = data.get("frage", "").strip()
        
        if not frage:
            return jsonify({"error": "Frage leer"}), 400
        
        antwort = sulee.antwort_generieren(frage)
        return jsonify({"antwort": antwort, "success": True})
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/set-mood", methods=["POST"])
def set_mood():
    """Setzt Sulees aktuelle Stimmung"""
    try:
        data = request.get_json()
        mood = data.get("mood", "neutral")
        sulee.engine.set_stimmung(mood)
        return jsonify({"success": True, "mood": mood})
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/status", methods=["GET"])
def status():
    """Liefert den aktuellen Status von Sulee"""
    try:
        return jsonify({
            "alter": sulee.engine.get_alter(),
            "stimmung": sulee.engine.get_stimmung(),
            "level": sulee.status.get("level", 1),
            "erfahrung": sulee.status.get("erfahrung", 0)
        })
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# ---------------------------------------------------------
# DEBUG ROUTES
# ---------------------------------------------------------

@app.route("/api/debug/backstory", methods=["GET"])
def debug_backstory():
    """Debug: Zeigt Sulees Backstory"""
    return jsonify(sulee.backstory)


@app.route("/api/debug/status", methods=["GET"])
def debug_status():
    """Debug: Zeigt vollständigen Status"""
    return jsonify(sulee.status)


if __name__ == "__main__":
    # Stelle sicher, dass templates/ existiert
    os.makedirs("templates", exist_ok=True)
    app.run(host="0.0.0.0", port=3554, debug=True)
