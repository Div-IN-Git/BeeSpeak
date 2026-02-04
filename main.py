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
 
    print("Honeypot Hit:")
    print(request_data)
 
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
