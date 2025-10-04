from schema import AccountSchema

def create_account(db, account_id, balance):
    new_account = AccountSchema(id=account_id, balance=balance)
    db.add(new_account)
    db.commit()
    db.refresh(new_account)
    return new_account

def handle_account_event(event, db):
    if event.type == "deposit":
        account = db.get(AccountSchema, event.destination)
        if account is None:
            new_account = create_account(db, event.destination, event.amount)
            return {"destination": {"id": str(new_account.id), "balance": new_account.balance}}
        else:
            account.balance += event.amount
            db.commit()
            db.refresh(account)
            return {"destination": {"id": str(account.id), "balance": account.balance}}

    elif event.type == "withdraw":
        account = db.get(AccountSchema, event.origin)
        if account is None:
            return None
        account.balance -= event.amount
        db.commit()
        db.refresh(account)
        return {"origin": {"id": str(account.id), "balance": account.balance}}

def handle_transaction_event(event, db):
    origin_account = db.get(AccountSchema, event.origin)
    destination_account = db.get(AccountSchema, event.destination)

    if origin_account is None:
        return None

    if destination_account is None:
        destination_account = create_account(db, event.destination, 0)

    origin_account.balance -= event.amount
    destination_account.balance += event.amount
    db.commit()
    db.refresh(origin_account)
    db.refresh(destination_account)
    return {
        "origin": {"id": str(origin_account.id), "balance": origin_account.balance},
        "destination": {"id": str(destination_account.id), "balance": destination_account.balance}
    }