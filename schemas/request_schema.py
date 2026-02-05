# schemas/request_schema.py

"""
Defines the expected structure of incoming requests.
Used only for validation / reference (no enforcement yet).
"""

REQUEST_SCHEMA = {
    "sessionId": str,
    "message": {
        "sender": str,       # "scammer" or "user"
        "text": str,
        "timestamp": int
    },
    "conversationHistory": list,
    "metadata": {
        "channel": str,      # SMS / WhatsApp / Email / Chat
        "language": str,     # English / Hindi / Tamil
        "locale": str        # IN, etc
    }
}
