import os

from datetime import datetime, timedelta, UTC
from typing import Optional, Dict, Any
from uuid import uuid4

from jose import jwt, JWTError
from passlib.context import CryptContext
from fastapi.security import OAuth2PasswordBearer
from app.core.exceptions import InvalidCredentialsError

SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = "HS256"

# sesijos galiojimo laikas, po kurio sesija uzsidaro
ACCESS_TOKEN_EXPIRE_MINUTES = 30

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/token")


pwd_context = CryptContext(
    schemes=["bcrypt"],
    deprecated="auto"
)
# passwordo hashinimas
def hash_password(password: str) -> str:
    return pwd_context.hash(password)
# passwordo tikrinimas
def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

# access tokeno kurimas, kuris bus naudojamas sessionui laikyti, tol kol baigiasi laikas
def create_access_token(
    subject: str,
    expires_delta: Optional[timedelta] = None
) -> str:
    
    now =datetime.now(UTC)
    
    if expires_delta:
        expire = now + expires_delta
    else:
        expire = now + timedelta(
            minutes=ACCESS_TOKEN_EXPIRE_MINUTES
        )

    to_encode: Dict[str, Any] = {
        "sub": subject,
        "exp": expire,
        "iat": datetime.now(UTC),
        'jti': str(uuid4())
    }

    encoded_jwt = jwt.encode(
        to_encode,
        SECRET_KEY,
        algorithm=ALGORITHM
    )
    return encoded_jwt
#  sesijos tokeno dekodavimas 
def decode_access_token(token: str) -> Dict[str, Any]:
    try:
        payload = jwt.decode(
            token,
            SECRET_KEY,
            algorithms=[ALGORITHM]
        )
        return payload
    except JWTError:
        raise InvalidCredentialsError
