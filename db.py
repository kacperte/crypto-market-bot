from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy import Column, Integer, String, DateTime, Float
from datetime import datetime

DATABASE_URL = "postgresql://kacper:password@localhost/info"
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autoflush=False, autocommit=False, bind=engine)
Base = declarative_base()


class NewToken(Base):
    __tablename__ = "info"
    id = Column(Integer, primary_key=True, index=True)
    instId = Column(String, index=True)
    date = Column(DateTime, default=datetime.utcnow())


class Transactions(Base):
    __tablename__ = "info"
    id = Column(Integer, primary_key=True, index=True)
    side = Column(String, index=True)
    ordId = Column(String, index=True)
    instId = Column(DateTime, default=datetime.utcnow())
    date = Column(DateTime, default=datetime.utcnow())


class SaleAlert(Base):
    __tablename__ = "info"
    id = Column(Integer, primary_key=True, index=True)
    type = Column(String, index=True)
    volumenOfSale = Column(Float, index=True)
    percent = Column(Float, index=True)
    price = Column(String, index=True)
    instId = Column(DateTime, default=datetime.utcnow())
    date = Column(DateTime, default=datetime.utcnow())


def add_to_new_token_db(session, instId):
    new_token = NewToken(
        details=instId,
        date=datetime.utcnow()
    )

    try:
        session.add(new_token)
        session.commit()
        session.refresh(new_token)
    finally:
        session.close()


def add_to_transaction_db(session, instId, side, ordId):
    new_transaction = Transactions(
        side=side,
        ordId=ordId,
        instId=instId,
        date=datetime.utcnow()
    )

    try:
        session.add(new_transaction)
        session.commit()
        session.refresh(new_transaction)
    finally:
        session.close()


def add_to_sales_alert_db(session, type, volumenOfSale, percent, price, instId):
    new_transaction = Transactions(
        type=type,
        volumenOfSale=volumenOfSale,
        percent=percent,
        price=price,
        instId=instId,
        date=datetime.utcnow()
    )

    try:
        session.add(new_transaction)
        session.commit()
        session.refresh(new_transaction)
    finally:
        session.close()

