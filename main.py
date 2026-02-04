from fastapi import FastAPI, Request, Header
from fastapi.responses import JSONResponse

app = FastAPI()

@app.api_route("/api/honeypot", methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"])
async def honeypot(
    request: Request,
    x_api_key: str = Header(default=None)
):
    # ---- API key check ----
    if not x_api_key:
        return JSONResponse(
            status_code=401,
            content={
                "status": "error",
                "reply": "Unauthorized request"
            }
        )

    # ---- Parse request body (GUVI sends valid JSON here) ----
    try:
        payload = await request.json()
    except Exception:
        return JSONResponse(
            status_code=400,
            content={
                "status": "error",
                "reply": "Invalid request body"
            }
        )

    # ---- Extract fields safely ----
    session_id = payload.get("sessionId")
    message = payload.get("message", {})
    conversation_history = payload.get("conversationHistory", [])

    incoming_text = message.get("text", "").lower()
    sender = message.get("sender", "unknown")

    # ---- Fake conversation history (for now, as requested) ----
    fake_history = conversation_history or [
        {
            "sender": "scammer",
            "text": "Your bank account will be blocked today.",
            "timestamp": 1769770000000
        }
    ]

    # ---- Simple scam intent detection (placeholder logic) ----
    scam_keywords = ["blocked", "verify", "urgent", "account", "upi", "bank"]
    scam_detected = any(word in incoming_text for word in scam_keywords)

    # ---- Agent reply generation (human-like, non-revealing) ----
    if scam_detected and sender == "scammer":
        reply_text = "Why is my account being suspended?"
    else:
        reply_text = "Can you please explain that again?"

    # ---- REQUIRED RESPONSE FORMAT (nothing extra) ----
    return JSONResponse(
        status_code=200,
        content={
            "status": "success",
            "reply": reply_text
        }
    )

