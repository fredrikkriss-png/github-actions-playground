import os
from pathlib import Path

# add this:
from dotenv import load_dotenv
env_path = Path(__file__).resolve().parent / ".env"
load_dotenv(env_path)  # loads variables from api/.env into os.environ

from fastapi import FastAPI, Header, HTTPException, Depends
from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime, timedelta
import jwt


app = FastAPI(title="Learning API", version="0.1.0")

# Read from environment (with safe dev defaults)
API_KEY = os.getenv("API_KEY", "dev-demo-key")
JWT_SECRET = os.getenv("JWT_SECRET", "dev-jwt-secret")
JWT_ALG = os.getenv("JWT_ALG", "HS256")
JWT_TTL_MIN = int(os.getenv("JWT_TTL_MIN", "10"))

class EchoIn(BaseModel):
    message: str = Field(min_length=1, max_length=280)
    uppercase: Optional[bool] = False

class EchoOut(BaseModel):
    message: str
    timestamp: str

def require_api_key(x_api_key: str = Header(..., alias="X-API-Key")):
    if x_api_key != API_KEY:
        raise HTTPException(status_code=401, detail="Invalid API key")
    return True

@app.get("/health")
def health():
    return {"status": "ok", "time": datetime.utcnow().isoformat()}

@app.post("/echo", response_model=EchoOut, dependencies=[Depends(require_api_key)])
def echo(payload: EchoIn):
    msg = payload.message.upper() if payload.uppercase else payload.message
    return EchoOut(message=msg, timestamp=datetime.utcnow().isoformat())

@app.post("/auth/token")
def issue_token(username: str):
    expiry = datetime.utcnow() + timedelta(minutes=JWT_TTL_MIN)
    token = jwt.encode({"sub": username, "exp": expiry}, JWT_SECRET, algorithm=JWT_ALG)
    return {"access_token": token, "token_type": "Bearer"}

def require_jwt(auth: Optional[str] = Header(None, alias="Authorization")):
    if not auth or not auth.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Missing token")
    token = auth.split(" ", 1)[1]
    try:
        return jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALG])
    except Exception:
        raise HTTPException(status_code=401, detail="Invalid/expired token")

@app.get("/me")
def me(claims: dict = Depends(require_jwt)):
    return {"you_are": claims.get("sub")}
