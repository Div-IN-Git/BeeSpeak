# schemas/response_schema.py

"""
Standard response format returned by the pipeline.
This will later be returned by the API endpoint.
"""

def base_response():
    return {
        "sessionId": None,
        "is_scam": False,
        "decision_source": None,   # "rule" or "ml"
        "confidence_score": 0.0,
        "category": None,
        "channel": None,
        "language": None,
        "locale": None,
        "session_context": {
            "channel": None,
            "language": None,
            "locale": None,
        },
        "agent_notes": "",
        "reasons": [],
        "extracted_entities": {
            "upi_ids": [],
            "phone_numbers": [],
            "phishing_links": [],
            "suspicious_keywords": [],
        }
    }
