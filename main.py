from fastapi import FastAPI, Request, Header
from fastapi.responses import Response
import datetime
import json
 
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
 
    print("Honeypot Hit:")
    print(request_data)
 
    if not x_api_key:
        response_payload = {
            "success": False,
            "message": "Missing x-api-key",
            "received": request_data,
        }
        return Response(
            status_code=401,
            content=json.dumps(response_payload, indent=2, ensure_ascii=False),
            media_type="application/json",
        )

    response_payload = {
        "success": True,
        "message": "Honeypot endpoint reached successfully",
        "received": request_data,
    }
    return Response(
        status_code=200,
        content=json.dumps(response_payload, indent=2, ensure_ascii=False),
        media_type="application/json",
    )
