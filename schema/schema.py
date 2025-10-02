from sqlalchemy import Column, Integer, Float
from sqlalchemy.orm import declarative_base

Base = declarative_base()

class AccountSchema(Base):
    __tablename__ = "account"

    id = Column(Integer, primary_key=True, autoincrement=False)
    balance = Column(Float, nullable=False)
