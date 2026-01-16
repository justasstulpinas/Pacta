
from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse

from app.database import engine, Base
from app.routers.auth import router as auth_router
from app.core.exceptions import (
    InvalidCredentialsError,
    PermissionDeniedError,
    NotFoundError
)

app = FastAPI(title="Pacta")

Base.metadata.create_all(bind=engine)

app.include_router(auth_router)

@app.exception_handler(InvalidCredentialsError)
def invalid_credentials_handler(request: Request, exc: InvalidCredentialsError):
    return JSONResponse(
        status_code= status.HTTP_401_UNAUTHORIZED,
        content={"detail": "Invalid email or password"},
    )

@app.exception_handler(PermissionDeniedError)
def permision_denied_handler(request: Request, exc: PermissionDeniedError):
    return JSONResponse(
        status_code= status.HTTP_403_FORBIDDEN,
        content={"detail": "Permision denied"},
    )

@app.exception_handler(NotFoundError)
def not_found_handler(request: Request, exc: NotFoundError):
    return JSONResponse(
        status_code= status.HTTP_404_NOT_FOUND,
        content={"detail": "Request not found"},
    )


@app.get("/")
def root():
    return {"status": "OK"}


@app.get("/health")
def health():
    return {"health": "alive"}


# Paleidus uvicorn app.main:app, python įkelia main.py, kuris importuoja engine ir Base iš database.py ir User modelį iš app.models.user.
# User klasė, paveldėdama iš Base, yra užregistruojama SQLAlchemy metaduomenyse.
# Base.metadata.create_all(bind=engine) peržiūri visus registruotus modelius ir, jei atitinkamų lentelių DB nėra, sukuria jas pagal modelių aprašus.
