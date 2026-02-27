from datetime import datetime, timedelta
import os
from uuid import uuid4
import blake3
from dotenv import load_dotenv
from fastapi.security import OAuth2PasswordBearer
import jwt

load_dotenv()
SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = os.getenv("ALGORITHM")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES"))

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")

def create_access_token(data: dict, expires_delta: int|None = None) -> str:
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta if expires_delta else timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": expire})
    encodet_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encodet_jwt

def create_refresh_token() -> tuple[str, str]:
    token =  uuid4()
    return token

def hash_refresh_token(token: str) -> str:
    hash = blake3.blake3((SECRET_KEY + token).encode()).hexdigest()
    return hash