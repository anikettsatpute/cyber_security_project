import sqlite3
import pandas as pd
from fastapi import FastAPI, HTTPException, Depends
from typing import List
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import jwt
from fastapi.security import OAuth2PasswordBearer
from passlib.context import CryptContext
import datetime

# Initialize FastAPI app
app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")
SECRET_KEY = "e7b3e7"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPI = 30

# password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

DATABASE = "ecommerce.db"

# JWT token
def create_access_token(data: dict, expires_delta: datetime.timedelta = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.datetime.utcnow() + expires_delta
    else:
        expire = datetime.datetime.utcnow() + datetime.timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def verify_token(token: str):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token has expired")
    except jwt.JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

@app.get("/")
def read_root():
    return {"Hello": "World"}

class login_req(BaseModel):
    user_id: str
    password: str

@app.post("/login")
def login(request: login_req):
    print(request)
    conn = sqlite3.connect(DATABASE)
    c = conn.cursor()
    
    # check if user exists
    c.execute("SELECT * FROM users WHERE user_id=?",(request.user_id,))
    user = c.fetchone()

    if user:
        if not verify_password(request.password, user[1]):
            conn.close()
            raise HTTPException(status_code=401, detail="Invalid credentials")
        else:
            access_token = create_access_token(data={"sub": request.user_id})
            conn.close()
            return {"access_token": access_token, "token_type": "bearer"}

    else:
        conn.close()
        raise HTTPException(status_code=401, detail="User does not exist")
    

class register_req(BaseModel):
    user_id: str
    password: str
    name: str
    email: str
    address: str
    phone_number: str

@app.post("/register")
def register(request: register_req):
    conn = sqlite3.connect(DATABASE)
    c = conn.cursor()
    
    # Check if user_id already exists
    c.execute("SELECT * FROM users WHERE user_id=?", (request.user_id,))
    user = c.fetchone()
    if user:
        conn.close()
        raise HTTPException(status_code=400, detail="User already exists")

    try:
        hashed_password = pwd_context.hash(request.password)
        c.execute('''
            INSERT INTO users (user_id, password, name, email, address, phone_number)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (request.user_id, hashed_password, request.name, request.email, request.address, request.phone_number))
    except Exception as e:
        conn.close()
        raise HTTPException(status_code=500, detail="Internal server error")

    conn.commit()
    conn.close()
    return {"message": "Registration successful"}