from typing import Union
from fastapi import FastAPI, Depends
from database import engine, get_db
from sqlalchemy import text
from sqlalchemy.orm import Session
from typing import Optional

app = FastAPI()

@app.get("/")
def read_root():
    return {"Hello": "World"}

@app.get("/balance?account_id={account_id}")
def read_account(account_id: int, db: Optional[Session] = Depends(get_db)):
    result = db.execute(
        text("SELECT * FROM account WHERE id = :id"),
        {"id": account_id}
    )
    account = result.fetchone()
    return {"account_id": account_id, "account": account}