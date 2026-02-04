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

    full_request_data = {
        "timestamp": datetime.datetime.utcnow().isoformat(),
        "method": request.method,
        "body": safe_body,
        "client_ip": request.client.host if request.client else "unknown",
        "url": str(request.url),
        "headers": dict(request.headers),
        "query_params": dict(request.query_params),
    }

    print("Honeypot Hit:")
    # print(full_request_data)

    allowed_header_keys = {
        "accept",
        "accept-encoding",
        "content-length",
        "content-type",
        "host",
        "user-agent",
        "x-api-key",
    }
    filtered_headers = {
        key: value
        for key, value in full_request_data["headers"].items()
        if key.lower() in allowed_header_keys
    }

    response_request_data = {
        **full_request_data,
        "headers": filtered_headers,
    }
 
    print("Honeypot Hit:")
    print(response_request_data)
 
    if not x_api_key:
        response_payload = {
            "success": False,
            "message": "Missing x-api-key",
            "received": response_request_data,
        }
        return Response(
            status_code=401,
            content=json.dumps(response_payload, indent=2, ensure_ascii=False),
            media_type="application/json",
        )

    response_payload = {
        "success": True,
        "message": "Honeypot endpoint reached successfully",
        "received": response_request_data,
    }
    return Response(
        status_code=200,
        content=json.dumps(response_payload, indent=2, ensure_ascii=False),
        media_type="application/json",
    )
