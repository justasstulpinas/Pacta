from fastapi import FastAPI
from app.database import engine, Base
from app.models import user

app = FastAPI(title="Pacta")

Base.metadata.create_all(bind=engine)

@app.get("/")
def root():
    return {"status": "OK"}

@app.get("/health")
def health():
    return {"health": "alive"}

# day