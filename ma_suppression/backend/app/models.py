from sqlalchemy import Column, Integer, String, Float, Date, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class Stock(Base):
    __tablename__ = "stocks"
    
    id = Column(Integer, primary_key=True, index=True)
    symbol = Column(String, unique=True, index=True)
    name = Column(String)
    market_cap = Column(Float)
    index_type = Column(String)  # "RUSSELL2000" or "NASDAQ"
    prices = relationship("StockPrice", back_populates="stock")
    suppression_scores = relationship("SuppressionScore", back_populates="stock")

class StockPrice(Base):
    __tablename__ = "stock_prices"
    
    id = Column(Integer, primary_key=True, index=True)
    stock_id = Column(Integer, ForeignKey("stocks.id"))
    date = Column(Date, index=True)
    open = Column(Float)
    high = Column(Float)
    low = Column(Float)
    close = Column(Float)
    stock = relationship("Stock", back_populates="prices")

class SuppressionScore(Base):
    __tablename__ = "suppression_scores"
    
    id = Column(Integer, primary_key=True, index=True)
    stock_id = Column(Integer, ForeignKey("stocks.id"))
    ma_period = Column(Integer)  # e.g., 20 for MA20
    score = Column(Float)
    contacts = Column(Integer)  # Number of contacts with MA
    breakthroughs = Column(Integer)  # Number of breakthroughs
    avg_deviation = Column(Float)  # Average deviation from MA
    stock = relationship("Stock", back_populates="suppression_scores")
