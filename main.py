from typing import Union
from fastapi import FastAPI, Depends
from sqlalchemy import text
from sqlalchemy.orm import Session
from typing import Optional

from database import engine, get_db
from controller import router

app = FastAPI()

@app.get("/")
def read_root():
    return {"Hello": "World"}

app.include_router(router)
