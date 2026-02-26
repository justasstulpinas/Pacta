from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse

from app.database import engine, Base
import app.models

from app.routers.auth import router as auth_router
from app.core.exceptions import (
    InvalidCredentialsError,
    PermissionDeniedError,
    NotFoundError,
    ForbiddenError
)
import os
from app.database import engine, Base
from app.models.contract_template import ContractTemplate
from app.routers.templates import router as templates_router
from app.routers import links

app = FastAPI(title="Pacta")

print("TABLES:", Base.metadata.tables.keys())
Base.metadata.create_all(bind=engine)

app.include_router(auth_router)
app.include_router(templates_router)
app.include_router(links.router)


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


@app.get("/")
def root():
    return {"status": "OK"}

@app.get("/health")
def health():
    return {"health": "alive"}

