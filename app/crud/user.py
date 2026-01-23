from sqlalchemy.orm import Session
from app.models.user import User

def create_user(db: Session, email: str, hashed_password: str) -> User:
    user =User(
        email = email,
        hashed_password = hashed_password
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user

def get_user_by_email(db: Session, email: str) -> User | None:
    return db.query(User).filter(User.email == email).first()

def get_user_by_id(db: Session, user_id: int) -> User | None:
    return db.query(User).filter(User.id == user_id).first()


# day4 sukurtas crud/user.py skirtas quierinti DB 
# crud darbas priimti, irasyti, atnaujinti duomenis, jis atleika veiksma su lentele