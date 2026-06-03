import os
from dotenv import load_dotenv
load_dotenv()
import app.models

from pathlib import Path
from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles

from app.database import engine, Base, SessionLocal
from app.routers.auth import router as auth_router
from app.routers import links, contracts, contacts
from app.routers.profile import router as profile_router
from app.routers.templates import router as templates_router
from app.core.exceptions import ValidationError
from app.core.exceptions import (
    InvalidCredentialsError,
    PermissionDeniedError,
    NotFoundError,
    ForbiddenError,
    UnauthorizedError,
    BadRequestError,
    RateLimitExceeded
)
from app.core.seed import seed_rbac
from slowapi import _rate_limit_exceeded_handler
from app.limiter import limiter



app = FastAPI(title="Pacta")
# next.js frontendo reikalai
app.add_middleware(
    CORSMiddleware,
    allow_origins=[os.getenv("FRONT_END_URL"), "http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
with SessionLocal() as db:
    seed_rbac(db)

app.include_router(auth_router)
app.include_router(templates_router)
app.include_router(links.router)
app.include_router(contacts.router)
app.include_router(profile_router)
app.include_router(contracts.router)
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)
app.state.limiter = limiter

uploads_dir = Path("app/uploads")
uploads_dir.mkdir(parents=True, exist_ok=True)
app.mount("/uploads", StaticFiles(directory=str(uploads_dir)), name="uploads")


@app.exception_handler(InvalidCredentialsError)
def invalid_credentials_handler(request: Request, exc: InvalidCredentialsError):
    return JSONResponse(
        status_code=status.HTTP_401_UNAUTHORIZED,
        content={"detail": "Invalid email or password"},
    )

@app.exception_handler(PermissionDeniedError)
def permission_denied_handler(request: Request, exc: PermissionDeniedError):
    return JSONResponse(
        status_code=status.HTTP_403_FORBIDDEN,
        content={"detail": "Permission denied"},
    )

@app.exception_handler(NotFoundError)
def not_found_handler(request: Request, exc: NotFoundError):
    return JSONResponse(
        status_code=status.HTTP_404_NOT_FOUND,
        content={"detail": "Request not found"},
    )

@app.exception_handler(ForbiddenError)
def forbidden_handler(_, __):
    return JSONResponse(
        status_code=403,
        content={"detail": "Forbidden"},
    )

@app.exception_handler(UnauthorizedError)
def unauthorized_handler(_, __):
    return JSONResponse(
        status_code=401,
        content={"detail": "Unauthorized"},
    )

@app.exception_handler(ValidationError)
def validation_error_handler(request: Request, exc: ValidationError):
    return JSONResponse(
        status_code=400,
        content={"detail": exc.detail},
    )

@app.exception_handler(BadRequestError)
def bad_request_handler(request: Request, exc: BadRequestError):
    return JSONResponse(
        status_code=400,
        content={"detail": "Bad request"},  
    )

app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

@app.get("/")
def root():
    return {"status": "OK"}

@app.get("/health")
def health():
    return {"health": "alive"}



