# libai
from fastapi import FastAPI, Depends
from sqlalchemy.orm import Session

# modeliai
from app.database import engine, Base, get_db
from app.models.user import User
from app.schemas import UserCreate
from app.security import hash_password




app = FastAPI(title="Pacta")

Base.metadata.create_all(bind=engine)

@app.get("/")
def root():
    return {"status": "OK"}

@app.get("/health")
def health():
    return {"health": "alive"}

# Paleidus uvicorn app.main:app, python įkelia main.py, kuris importuoja engine ir Base iš database.py ir User modelį iš app.models.user.
# User klasė, paveldėdama iš Base, yra užregistruojama SQLAlchemy metaduomenyse.
# Base.metadata.create_all(bind=engine) peržiūri visus registruotus modelius ir, jei atitinkamų lentelių DB nėra, sukuria jas pagal modelių aprašus.

@app.get('/users/count/')
def users_count(db: Session = Depends(get_db)):
    return{'users': db.query(User).count()}

# sukurta sesija patikrinti ar veikia user requestai

# sukuriamas linkas uzregistruoti useri
@app.post("/register")
def register_user(
    user_data: UserCreate,
    db: Session = Depends(get_db)
):
    existing_user = db.query(User).filter(User.email == user_data.email).first()
    if existing_user:
        return {"error": "User already exists"}
    
    new_user = User(
        email = user_data.email,
        hashed_password = hash_password(user_data.password)
    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return{
        "id": new_user.id,
        "email": new_user.email
    }