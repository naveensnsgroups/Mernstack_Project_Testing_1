from fastapi import FastAPI, Request, status, HTTPException
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from config.settings import settings
from config.db import connect_db, close_db
from routes.employee_routes import router as employee_router
import time

request_counts = {}

@asynccontextmanager
async def lifespan(app: FastAPI):
    await connect_db()
    yield
    await close_db()

app = FastAPI(
    title="Personal Details API",
    version="1.0.0",
    lifespan=lifespan
)

allowed_origins = [url.strip().rstrip('/') for url in settings.client_url.split(',')]

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins if '*' not in allowed_origins else ['*'],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["Content-Type"],
)

@app.middleware("http")
async def security_and_rate_limit_middleware(request: Request, call_next):
    if request.method in ["POST", "PUT"]:
        content_length = request.headers.get("content-length")
        if content_length and int(content_length) > 10 * 1024:
            return JSONResponse(
                status_code=413,
                content={"success": False, "message": "Payload too large (max 10kb)"}
            )

    if request.url.path.startswith("/api"):
        client_ip = request.client.host if request.client else "unknown"
        current_time = time.time()
        window_duration = 15 * 60
        max_requests = 100

        if client_ip not in request_counts:
            request_counts[client_ip] = {"count": 1, "reset_time": current_time + window_duration}
        else:
            data = request_counts[client_ip]
            if current_time > data["reset_time"]:
                data["count"] = 1
                data["reset_time"] = current_time + window_duration
            else:
                data["count"] += 1
                if data["count"] > max_requests:
                    return JSONResponse(
                        status_code=429,
                        headers={"Retry-After": str(int(data["reset_time"] - current_time))},
                        content={"success": False, "message": "Too many requests, please try again later."}
                    )

    response = await call_next(request)
    return response

app.include_router(employee_router)

@app.get("/", status_code=status.HTTP_200_OK)
async def root_health_check():
    return {"success": True, "message": "Personal Details API is running."}

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    messages = []
    for error in exc.errors():
        msg = error.get("msg", "")
        # Remove 'Value error, ' prefix if added by pydantic field_validator
        if msg.startswith("Value error, "):
            msg = msg[len("Value error, "):]
        messages.append(msg)
    return JSONResponse(
        status_code=400,
        content={"success": False, "message": ", ".join(messages)}
    )

@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    return JSONResponse(
        status_code=exc.status_code,
        content={"success": False, "message": str(exc.detail)}
    )

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    error_msg = str(exc)
    status_code = getattr(exc, "status_code", 500)
    
    if settings.node_env == "production" and status_code == 500:
        error_msg = "Internal Server Error"

    return JSONResponse(
        status_code=status_code,
        content={"success": False, "message": error_msg}
    )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=settings.port, reload=True)
