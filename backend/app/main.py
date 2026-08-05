import logging
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError

from app.api.routes import router
from app.core.config import get_settings

logging.basicConfig(level=logging.INFO)
settings = get_settings()

app = FastAPI(title="AI Research Agent API")


app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # Next.js dev server
    allow_methods=["POST"],
    allow_headers=["Content-Type"],
)


@app.exception_handler(RequestValidationError)
async def validation_error_handler(request: Request, exc: RequestValidationError):
    """Ensures a blank/missing topic returns our own ErrorResponse shape
    (§3.3 of the frontend brief), not FastAPI's default validation error
    format — keeps the error contract consistent across every failure mode."""
    return JSONResponse(
        status_code=400,
        content={"error": {"code": "INVALID_REQUEST", "message": "Please enter a topic to research."}},
    )


app.include_router(router, prefix="/api")