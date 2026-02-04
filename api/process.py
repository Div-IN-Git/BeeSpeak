import os
import sys
from flask import Flask, request, jsonify

# Ensure project root is importable
sys.path.append(os.getcwd())

from core.pipeline import process_message

app = Flask(__name__)

API_KEY = os.environ.get("HONEY_POT_API_KEY", "guvi-honeypot-2026")


@app.route("/", methods=["GET", "POST"])
def index():
    # ---------- AUTH ----------
    incoming_key = request.headers.get("x-api-key")

    if not incoming_key:
        return jsonify({"error": "Missing x-api-key"}), 401

    if incoming_key != API_KEY:
        return jsonify({"error": "Invalid API key"}), 401

    # ---------- HEALTH ----------
    if request.method == "GET":
        return jsonify({
            "status": "SUCCESS",
            "service": "BeeSpeak Honeypot API"
        })

    # ---------- POST ----------
    data = request.get_json(silent=True)
    if not data:
        return jsonify({"error": "Invalid JSON body"}), 400

    try:
        result = process_message(data)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

    return jsonify(result)
