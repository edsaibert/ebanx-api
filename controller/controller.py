from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import text
from sqlalchemy.orm import Session

from database import engine, get_db
from models import Account, Event
from schema import AccountSchema

router = APIRouter(prefix="", tags=["all"])

@router.get("/balance")
def get_balance(account_id: int, db: Session = Depends(get_db)):
    result = db.execute(
        text("SELECT * FROM account WHERE id = :id"),
        {"id": account_id}
    )
    account = result.fetchone()

    if account is not None:
        return {"balance": account.balance}
    else:
        # return 404
        raise HTTPException(
            status_code = 404,
            detail = 0
        )
    
@router.post("/event")
def post_event(event: Event, db: Session = Depends(get_db)):
    if event.type == "deposit" or event.type == "withdraw":
        ret = handle_account_event(event, db)
    elif event.type == "transfer":
        ret = handle_transaction_event(event, db)
    else:
        raise HTTPException(
            status_code = 400,
            detail = "Invalid event type"
        )
    return ret

def create_account(db: Session, account_id: int, balance: float):
    new_account = AccountSchema(id=account_id, balance=balance)
    db.add(new_account)
    db.commit()
    db.refresh(new_account)
    return new_account

def handle_account_event(event: Event, db: Session):
    if event.type == "deposit":
        # check if account exists
        account = db.get(AccountSchema, event.origin)
        if account is None:
            # create account
            new_account = create_account(db, event.origin, event.amount)
            return {"destination": {"id": new_account.id, "balance": new_account.balance}}
        
        else:
            # update account balance
            account.balance += event.amount
            db.commit()
            db.refresh(account)
            return {"destination": {"id": account.id, "balance": account.balance}}

    elif event.type == "withdraw":
        account = db.get(AccountSchema, event.origin)
        # check if account exists
        if account is None:
            raise HTTPException(
                status_code = 404,
                detail = 0
            )
        
        # update account balance
        account.balance -= event.amount
        db.commit()
        db.refresh(account)

        return {"origin": {"id": account.id, "balance": account.balance}}


def handle_transaction_event(event: Event, db: Session):
    origin_account = db.get(AccountSchema, event.origin)
    destination_account = db.get(AccountSchema, event.destination)

    # check if origin account exists
    if origin_account is None:
        raise HTTPException(
            status_code = 404,
            detail = 0
        )
    
    # check if destination account exists
    if destination_account is None:
        # create destination account
        destination_account = create_account(db, event.destination, 0)

    # update balances
    origin_account.balance -= event.amount
    destination_account.balance += event.amount
    db.commit()
    db.refresh(origin_account)
    db.refresh(destination_account)
    return {
        "origin": {"id": origin_account.id, "balance": origin_account.balance},
        "destination": {"id": destination_account.id, "balance": destination_account.balance}
    }