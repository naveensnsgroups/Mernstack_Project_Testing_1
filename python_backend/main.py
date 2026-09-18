import os
from contextlib import asynccontextmanager
from pathlib import Path
from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

from python_backend.config.db import connect_db, close_db
from python_backend.routes.employee_routes import router as employee_router

load_dotenv(Path(__file__).resolve().parent / ".env")

@asynccontextmanager
async def lifespan(app: FastAPI):
    await connect_db()
    yield
    await close_db()

app = FastAPI(
    title="Personal Details API",
    description="Python FastAPI backend migrated from Express.js",
    version="1.0.0",
    lifespan=lifespan
)

raw_client_url = os.getenv("CLIENT_URL", "http://localhost:5173")
allowed_origins = [url.strip().rstrip("/") for url in raw_client_url.split(",")]
origins = ["*"] if "*" in allowed_origins else allowed_origins

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["Content-Type"],
)

app.include_router(employee_router)

@app.get("/", status_code=status.HTTP_200_OK)
async def root():
    return {"success": True, "message": "Personal Details API is running."}

@app.exception_handler(404)
async def not_found_handler(request: Request, exc):
    return JSONResponse(
        status_code=404,
        content={"success": False, "message": "Route not found"}
    )

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    error_messages = []
    for err in exc.errors():
        msg = err.get("msg", "Validation error")
        if msg.startswith("Value error, "):
            msg = msg[len("Value error, "):]
        error_messages.append(msg)
    
    joined_msg = ", ".join(error_messages) if error_messages else "Validation error"
    
    cleaned_errors = []
    for err in exc.errors():
        err_copy = dict(err)
        if "ctx" in err_copy:
            ctx = {}
            for k, v in err_copy["ctx"].items():
                if isinstance(v, Exception):
                    ctx[k] = str(v)
                else:
                    ctx[k] = v
            err_copy["ctx"] = ctx
        cleaned_errors.append(err_copy)

    return JSONResponse(
        status_code=400,
        content={"success": False, "message": joined_msg, "errors": cleaned_errors}
    )

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc):
    print(f"[ERROR] {request.method} {request.url.path} — {str(exc)}")
    status_code = getattr(exc, "status_code", 500)
    detail = getattr(exc, "detail", None)
    
    if isinstance(detail, dict):
        return JSONResponse(status_code=status_code, content=detail)
    
    message = detail if detail else (
        "Internal Server Error" if os.getenv("NODE_ENV") == "production" else str(exc)
    )
    return JSONResponse(
        status_code=status_code,
        content={"success": False, "message": message}
    )
