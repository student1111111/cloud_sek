from typing import Optional

from sqlalchemy import Column, Integer, String, Float
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from contextlib import contextmanager

Base = declarative_base()

class User(Base):
    __tablename__ = "user_table"
    user_name = Column(String(100),
                    primary_key=True,
                    nullable=False)
    password = Column(String(100),
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
    def get_user(self, session, user_name):
        return session.query(User).get(user_name)

    def add_user(self, session, user):
        session.add(user)

from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.security import OAuth2PasswordBearer

from passlib.context import CryptContext
from pydantic import BaseModel

import random

app = FastAPI()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password):
    return pwd_context.hash(password)

class Account(BaseModel):
    user_name : str
    password: str

@app.post("/register")
async def register_user(account: Account):
    new_user = User(user_name=account.user_name,
                password=get_password_hash(account.password))

    with session_scope() as session:
        user = DbOps().get_user(session, account.user_name)
        if not user:
            DbOps().add_user(session, new_user)
        else:
            print("ASK")
            print(user)
            raise HTTPException(status_code=409, detail="User {} already exists".format(account.user_name))
    return account

@app.get("/APIA")
def read_root():
    return random.randint(0,100)
