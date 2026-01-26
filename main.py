from fastapi import FastAPI, Request, Header
import os
import json

app = FastAPI()

@app.post("/test")
async def test_endpoint(
    request: Request,
    x_api_key: str = Header(default=None)
):
    # ---- AUTH (OPTIONAL FOR NOW) ----
    if x_api_key != os.getenv("HONEYPOT_API_KEY"):
        return {
            "status": "error",
            "error": "Unauthorized"
        }

    # ---- RAW BODY ----
    raw_body = None
    try:
        raw_body = await request.body()
    except:
        raw_body = b""

    # ---- TRY JSON PARSE ----
    parsed_json = None
    try:
        parsed_json = json.loads(raw_body.decode("utf-8"))
    except:
        parsed_json = None

    # ---- LOG EVERYTHING ----
    print("\n========== NEW REQUEST ==========")
    print("Headers:")
    print(dict(request.headers))
    print("\nRaw Body:")
    print(raw_body)
    print("\nParsed JSON:")
    print(parsed_json)
    print("=================================\n")

    # ---- ALWAYS RETURN VALID JSON ----
    return {
        "status": "ok",
        "received": True
    }

