from fastapi import FastAPI, Request, Header
from fastapi.responses import JSONResponse

app = FastAPI()

# -------- GET: reachability check --------
@app.get("/api/honeypot")
async def honeypot_get():
    return {
        "status": "success",
        "reply": "Can you explain what you mean?"
    }

# -------- POST: agentic honeypot --------
@app.post("/api/honeypot")
async def honeypot_post(
    request: Request,
    x_api_key: str = Header(default=None)
):
    if not x_api_key:
        return JSONResponse(
            status_code=401,
            content={
                "status": "error",
                "reply": "Unauthorized"
            }
        )

    try:
        payload = await request.json()
    except Exception:
        return JSONResponse(
            status_code=400,
            content={
                "status": "error",
                "reply": "Invalid request"
            }
        )

    message = payload.get("message", {})
    text = message.get("text", "").strip()
    sender = message.get("sender", "").lower()

    # ---- Simple scam intent detection ----
    scam_triggers = [
        "account", "blocked", "verify", "urgent",
        "upi", "bank", "suspend", "limited"
    ]

    is_scam = (
        sender == "scammer"
        and any(word in text.lower() for word in scam_triggers)
    )

    # ---- Dynamic, human-like replies ----
    if is_scam:
        if "account" in text.lower():
            reply = "Why is my account being blocked?"
        elif "upi" in text.lower():
            reply = "Why do you need my UPI ID?"
        elif "verify" in text.lower():
            reply = "What exactly do I need to verify?"
        else:
            reply = "Can you explain this in more detail?"
    else:
        reply = "I’m not sure I understand. Can you clarify?"

    return {
        "status": "success",
        "reply": reply
    }
