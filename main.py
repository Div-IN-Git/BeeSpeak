# from fastapi import FastAPI, Request, Header
# import os
# import json

# app = FastAPI()

# @app.post("/test")
# async def test_endpoint(
#     request: Request,
#     x_api_key: str = Header(default=None)
# ):
#     # ---- AUTH (OPTIONAL FOR NOW) ----
#     if x_api_key != os.getenv("HONEYPOT_API_KEY"):
#         return {
#             "status": "error",
#             "error": "Unauthorized"
#         }

#     # ---- RAW BODY ----
#     raw_body = None
#     try:
#         raw_body = await request.body()
#     except:
#         raw_body = b""

#     # ---- TRY JSON PARSE ----
#     parsed_json = None
#     try:
#         parsed_json = json.loads(raw_body.decode("utf-8"))
#     except:
#         parsed_json = None

#     # ---- LOG EVERYTHING ----
#     print("\n========== NEW REQUEST ==========")
#     print("Headers:")
#     print(dict(request.headers))
#     print("\nRaw Body:")
#     print(raw_body)
#     print("\nParsed JSON:")
#     print(parsed_json)
#     print("=================================\n")

#     # ---- ALWAYS RETURN VALID JSON ----
#     return {
#         "status": "ok",
#     "received": True
# }

from fastapi import FastAPI, Request, Header
from fastapi.responses import JSONResponse
import datetime

app = FastAPI()

@app.api_route("/api/honeypot", methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"])
async def honeypot(
    request: Request,
    x_api_key: str = Header(default=None)
):
    body = None
    try:
        body = await request.json()
    except:
        body = await request.body()

    safe_body = (
        body.decode("utf-8", errors="replace")
        if isinstance(body, bytes)
        else body
    )

    request_data = {
        "timestamp": datetime.datetime.utcnow().isoformat(),
        "method": request.method,
        "url": str(request.url),
        "headers": dict(request.headers),
        "query_params": dict(request.query_params),
        "body": safe_body,
        "client_ip": request.client.host if request.client else "unknown",
    }

    # 🔥 Logs appear in Vercel logs
    print("🔥 Honeypot Hit:")
    print(request_data)

    # Optional: x-api-key check (their form requires it)
    if not x_api_key:
        return JSONResponse(
            status_code=401,
            content={
                "success": False,
                "message": "Missing x-api-key",
                "received": request_data
            }
        )

    return JSONResponse(
        status_code=200,
        content={
            "success": True,
            "message": "Honeypot endpoint reached successfully",
            "received": request_data
        }
    )



