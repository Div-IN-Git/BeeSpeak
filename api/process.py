# api/process.py

import json
import os
import sys

# Make project root importable
sys.path.append(os.getcwd())

from core.pipeline import process_message

API_KEY = os.environ.get("HONEY_POT_API_KEY", "guvi-honeypot-2026")


def main(request):
    # -------- HEADERS --------
    headers = {k.lower(): v for k, v in (request.headers or {}).items()}
    incoming_key = headers.get("x-api-key")

    if not incoming_key:
        return {
            "statusCode": 401,
            "headers": {"Content-Type": "application/json"},
            "body": json.dumps({"error": "Missing x-api-key"})
        }

    if incoming_key != API_KEY:
        return {
            "statusCode": 401,
            "headers": {"Content-Type": "application/json"},
            "body": json.dumps({"error": "Invalid API key"})
        }

    # -------- GET (Health) --------
    if request.method == "GET":
        return {
            "statusCode": 200,
            "headers": {"Content-Type": "application/json"},
            "body": json.dumps({
                "status": "SUCCESS",
                "service": "BeeSpeak Honeypot API"
            })
        }

    # -------- POST ONLY --------
    if request.method != "POST":
        return {
            "statusCode": 405,
            "headers": {"Content-Type": "application/json"},
            "body": json.dumps({"error": "Method not allowed"})
        }

    # -------- BODY --------
    try:
        payload = json.loads(request.body)
    except Exception:
        return {
            "statusCode": 400,
            "headers": {"Content-Type": "application/json"},
            "body": json.dumps({"error": "Invalid JSON body"})
        }

    # -------- PIPELINE --------
    try:
        result = process_message(payload)
    except Exception as e:
        return {
            "statusCode": 500,
            "headers": {"Content-Type": "application/json"},
            "body": json.dumps({"error": str(e)})
        }

    return {
        "statusCode": 200,
        "headers": {"Content-Type": "application/json"},
        "body": json.dumps(result)
    }
