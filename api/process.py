# api/process.py

import json
import os
import sys
sys.path.append(os.getcwd())

from core.pipeline import process_message

# API KEY (set this in Vercel Environment Variables)
API_KEY = os.environ.get("HONEY_POT_API_KEY", "guvi-honeypot-2026")


def handler(request):
    # -----------------------------
    # 1. API KEY AUTH
    # -----------------------------
    headers = {k.lower(): v for k, v in (request.headers or {}).items()}
    incoming_key = headers.get("x-api-key")

    if not incoming_key:
        return {
            "statusCode": 401,
            "body": json.dumps({"error": "Missing x-api-key"})
        }

    if incoming_key != API_KEY:
        return {
            "statusCode": 401,
            "body": json.dumps({"error": "Invalid API key"})
        }

    # -----------------------------
    # 2. GET → Health check
    # -----------------------------
    if request.method == "GET":
        return {
            "statusCode": 200,
            "body": json.dumps({
                "status": "SUCCESS",
                "service": "BeeSpeak Honeypot API"
            })
        }

    # -----------------------------
    # 3. POST → Main processing
    # -----------------------------
    if request.method != "POST":
        return {
            "statusCode": 405,
            "body": json.dumps({"error": "Method not allowed"})
        }

    # -----------------------------
    # 4. READ BODY (VERCEL SAFE)
    # -----------------------------
    try:
        payload = json.loads(request.body)
    except Exception:
        return {
            "statusCode": 400,
            "body": json.dumps({"error": "Invalid JSON body"})
        }

    # -----------------------------
    # 5. PIPELINE CALL
    # -----------------------------
    try:
        response = process_message(payload)
    except Exception as e:
        return {
            "statusCode": 500,
            "body": json.dumps({"error": str(e)})
        }

    # -----------------------------
    # 6. RETURN JSON
    # -----------------------------
    return {
        "statusCode": 200,
        "headers": {"Content-Type": "application/json"},
        "body": json.dumps(response)
    }
