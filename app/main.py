
from fastapi import FastAPI

from app.database import engine, Base
from app.routers.auth import router as auth_router

app = FastAPI(title="Pacta")

# DB inicializacija (dev režimas)
Base.metadata.create_all(bind=engine)

# Routerių prijungimas
app.include_router(auth_router)


@app.get("/")
def root():
    return {"status": "OK"}


@app.get("/health")
def health():
    return {"health": "alive"}


# Paleidus uvicorn app.main:app, python įkelia main.py, kuris importuoja engine ir Base iš database.py ir User modelį iš app.models.user.
# User klasė, paveldėdama iš Base, yra užregistruojama SQLAlchemy metaduomenyse.
# Base.metadata.create_all(bind=engine) peržiūri visus registruotus modelius ir, jei atitinkamų lentelių DB nėra, sukuria jas pagal modelių aprašus.
