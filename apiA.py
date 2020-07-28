from typing import Optional

from sqlalchemy import Column, Integer, String, Float
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy import update

from contextlib import contextmanager

Base = declarative_base()

class User(Base):
    __tablename__ = "user_table"
    username  = Column(String(100),
                    primary_key=True,
                    nullable=False)
    password   = Column(String(100),
                    nullable=False)
    api_tokens = Column(Integer,
                    nullable=False)
    time_stamp = Column(Integer,
                    nullable=False) 
    
engine = create_engine("sqlite:///users.db", echo=True)
Base.metadata.create_all(engine)

Session = sessionmaker(bind=engine)

'''
https://docs.sqlalchemy.org/en/13/orm/session_basics.html
'''
@contextmanager
def session_scope():
    """Provide a transactional scope around a series of operations."""
    session = Session()
    try:
        yield session
        session.commit()
    except:
        session.rollback()
        raise
    finally:
        session.close()

class DbOps(object):
    def get_user(self, session, username):
        return session.query(User).get(username)

    def add_user(self, session, user):
        session.add(user)

    def update_user(self, session, user):
        old = session.query(User).get(user.username)
        old.api_tokens = user.api_tokens
        old.time_stamp = user.time_stamp

from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm

from jose import JWTError, jwt

from passlib.context import CryptContext
from datetime import datetime, timedelta
from pydantic import BaseModel

import random
import time
import copy

# openssl rand -hex 32
SECRET_KEY = "8f691c89e057643a3090a25cef97b3e0a30285ae1e23c046cc87d0cbc7abd89d"
ALGORITHM = "HS256"
# one day expiration
ACCESS_TOKEN_EXPIRE_MINUTES = 3600*24

app = FastAPI()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password):
    return pwd_context.hash(password)

class Account(BaseModel):
    username : str
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: Optional[str] = None

def authenticate_user(username: str, password: str):
    with session_scope() as session:
        user = DbOps().get_user(session, username)
        if not user:
            return False
        if not verify_password(password, user.password):
            return False
        print("Authenticated {}".format(user.username))
        return user
    return False

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

async def get_current_user(token: str = Depends(oauth2_scheme)):
    credentials_exception = HTTPException(
        status_code=403,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        token_data = TokenData(username=username)
    except JWTError:
        raise credentials_exception
    with session_scope() as session:
        user = DbOps().get_user(session, token_data.username)
        if not user:
            raise credentials_exception
        # update the token calculation before returning
        time_stamp = int(time.time())
        if ((time_stamp - user.time_stamp) > 60):
            user.api_tokens  = 5
            user.time_stamp  = time_stamp
        return copy.deepcopy(user)
    raise credentials_exception

async def get_current_active_user(current_user: User = Depends(get_current_user)):
    return current_user

def update_api_token(user : User):
    new_token_size = 5
    time_stamp = int(time.time())
    if ((time_stamp - user.time_stamp) < 60):
        # a minite has not passed, take from token bucket
        new_token_size = user.api_tokens - 1
    user.time_stamp = time_stamp
    user.api_tokens = new_token_size

    with session_scope() as session:
        DbOps().update_user(session, user)

@app.post("/register")
async def register_user(account: Account):
    new_user = User(username=account.username,
                password=get_password_hash(account.password),
                api_tokens=5,
                time_stamp=int(time.time()))

    with session_scope() as session:
        user = DbOps().get_user(session, account.username)
        if not user:
            DbOps().add_user(session, new_user)
        else:
            raise HTTPException(status_code=409, detail="User {} already exists".format(account.username))
    return "Successfully registered {}".format(account.username)

@app.post("/login", response_model=Token)
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()):
    user = authenticate_user(form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=403,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": form_data.username}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}

@app.get("/call_api")
async def call_get_number(current_user: User = Depends(get_current_active_user)):
    rate_limit_exception = HTTPException(
        status_code=403,
        detail="API rate limit excceded",
        headers={"WWW-Authenticate": "Bearer"},
    )
    if current_user.api_tokens <1:
        raise rate_limit_exception

    update_api_token(current_user)
    return get_number()

@app.get("/see_remaining_limit")
async def get_limit(current_user: User = Depends(get_current_active_user)):
    return current_user.api_tokens

'''
Random Number Geretator 
'''
def get_number():
    return random.randint(0,100)

