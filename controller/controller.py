import json
from fastapi import APIRouter, Depends, HTTPException, Response, status
from sqlalchemy import text
from sqlalchemy.orm import Session

from database import engine, get_db
from models import Account, Event
from schema import AccountSchema
from service import handle_account_event, handle_transaction_event

router = APIRouter(prefix="", tags=["all"])

@router.post("/reset")
def reset_state(db: Session = Depends(get_db)):
    db.execute(text("DELETE FROM account"))
    db.commit()
    return Response(content="OK", status_code=200)

@router.get("/balance")
def get_balance(account_id: int, db: Session = Depends(get_db)):
    account = db.get(AccountSchema, account_id)  # Use ORM instead of raw SQL
    if account is not None:
        return Response(content=str(account.balance), status_code=200)
    else:
        return Response(content="0", status_code=404)
    
@router.post("/event")
def post_event(event: Event, db: Session = Depends(get_db)):
    try:
        if event.type == "deposit" or event.type == "withdraw":
            ret = handle_account_event(event, db)
            if ret is None:
                return Response(content="0", status_code=404)
        elif event.type == "transfer":
            ret = handle_transaction_event(event, db)
            if ret is None:
                return Response(content="0", status_code=404)
        else:
            return Response(content="0", status_code=400)
        return Response(content=json.dumps(ret), status_code=201, media_type="application/json")
    except HTTPException as e:
        if e.status_code == 404:
            return Response(content="0", status_code=404)
        raise