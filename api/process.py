# api/process.py

import os
import json
import sys
from flask import Flask, request, jsonify

# Ensure project root is importable
sys.path.append(os.getcwd())

from core.pipeline import process_message

app = Flask(__name__)

API_KEY = os.environ.get("HONEY_POT_API_KEY", "guvi-honeypot-2026")


@app.route("/api/process", methods=["GET", "POST"])
def process():
    # ---------------- AUTH ----------------
    incoming_key = request.headers.get("x-api-key")

    if not incoming_key:
        return jsonify({"error": "Missing x-api-key"}), 401

    if incoming_key != API_KEY:
        return jsonify({"error": "Invalid API key"}), 401

    # ---------------- GET (Health) ----------------
    if request.method == "GET":
        return jsonify({
            "status": "SUCCESS",
            "service": "BeeSpeak Honeypot API"
        }), 200

    # ---------------- POST ----------------
    try:
        payload = request.get_json(force=True)
    except Exception:
        return jsonify({"error": "Invalid JSON body"}), 400

    try:
        response = process_message(payload)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

    return jsonify(response), 200
