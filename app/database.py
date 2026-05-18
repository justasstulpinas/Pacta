import os

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base, Session
from typing import Generator

DATABASE_URL = os.getenv("DATABASE_URL")

engine = create_engine(
    DATABASE_URL, connect_args={"check_same_thread": False}
)

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)

Base =declarative_base()

# sukurta duombaze pacta/app/pacta.db

def get_db() -> Generator[Session, None, None]:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# per get_db() FastAPI kiekvienam http requestui sukuria atskirą sqlalchemy sesija, kuri naudojama DB operacijoms atlikti,
# pasibaigus requestui sesija automatiskai uzdaroma, todel kiekvienas vartotjas veiksmus atlieka tik savo sesijoje.
#  kiekvienas useris gali requesta daryti kiek nori kartu nes visada sukuriamas naujas http requestas.