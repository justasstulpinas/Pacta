from fastapi import FastAPI

app = FastAPI(title="Pacta")

@app.get("/")
def root():
    return {"status": "OK"}

@app.get("/health")
def health():
    return {"health": "alive"}