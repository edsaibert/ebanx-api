from pydantic import BaseModel
from typing import Optional 

class Account(BaseModel):
    id: int
    balance: float

class Event(BaseModel):
    type: str
    origin: Optional[int] = None
    destination: Optional[int] = None
    amount: float
 