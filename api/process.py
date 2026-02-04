# api/process.py
import os
import sys
import json
import traceback

# make sure project root is importable
sys.path.append(os.getcwd())

API_KEY = os.environ.get("HONEY_POT_API_KEY", "guvi-honeypot-2026")

def _json_resp(status, body):
    return {
        "statusCode": status,
        "headers": {"Content-Type": "application/json"},
        "body": json.dumps(body)
    }

def handler(request):
    # quick debug info
    try:
        _debug = {
            "cwd": os.getcwd(),
            "sys_path_head": sys.path[:5],
            "env_keys": ["HONEY_POT_API_KEY" in os.environ]
        }
    except Exception:
        _debug = {"cwd": None}

    # auth
    headers = {k.lower(): v for k, v in (request.headers or {}).items()}
    incoming_key = headers.get("x-api-key")
    if not incoming_key:
        return _json_resp(401, {"error": "Missing x-api-key", "debug": _debug})

    if incoming_key != API_KEY:
        return _json_resp(401, {"error": "Invalid x-api-key", "debug": _debug})

    if request.method == "GET":
        return _json_resp(200, {"status": "ok", "service": "BeeSpeak Honeypot API", "debug": _debug})

    if request.method != "POST":
        return _json_resp(405, {"error": "Method not allowed", "debug": _debug})

    # parse body safely
    try:
        payload = json.loads(request.body)
    except Exception as ex:
        tb = traceback.format_exc()
        return _json_resp(400, {"error": "Invalid JSON body", "detail": str(ex), "trace": tb, "debug": _debug})

    # Lazy import pipeline to capture import errors cleanly
    try:
        from core.pipeline import process_message
    except Exception as ex:
        tb = traceback.format_exc()
        return _json_resp(500, {
            "error": "ImportError in core.pipeline",
            "detail": str(ex),
            "traceback": tb,
            "debug": _debug
        })

    # Run pipeline and catch errors
    try:
        result = process_message(payload)
    except Exception as ex:
        tb = traceback.format_exc()
        return _json_resp(500, {
            "error": "Pipeline runtime error",
            "detail": str(ex),
            "traceback": tb,
            "debug": _debug
        })

    return _json_resp(200, result)
