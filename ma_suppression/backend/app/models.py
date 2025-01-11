from sqlalchemy import Column, Integer, String, Float, Date, ForeignKey, Index
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class Stock(Base):
    __tablename__ = "stocks"
    
    id = Column(Integer, primary_key=True, index=True)
    symbol = Column(String(10), index=True)  # Removed unique constraint
    name = Column(String(100), index=True)
    market_cap = Column(Float, index=True)  # Indexed for filtering by market cap
    index_type = Column(String(20), index=True)  # "RUSSELL2000" or "NASDAQ", indexed for filtering
    prices = relationship("StockPrice", back_populates="stock")
    suppression_scores = relationship("SuppressionScore", back_populates="stock")
    
    __table_args__ = (
        # Composite unique constraint for symbol + index_type
        Index('idx_symbol_index', 'symbol', 'index_type', unique=True),
    )

class StockPrice(Base):
    __tablename__ = "stock_prices"
    
    id = Column(Integer, primary_key=True, index=True)
    stock_id = Column(Integer, ForeignKey("stocks.id"), index=True)
    date = Column(Date, index=True)
    open = Column(Float)
    high = Column(Float)
    low = Column(Float)
    close = Column(Float, index=True)  # Index for quick price lookups
    stock = relationship("Stock", back_populates="prices")
    
    __table_args__ = (
        # Composite index for efficient time series queries
        Index('idx_stock_date', 'stock_id', 'date'),
        # Index for date-based queries
        Index('idx_stock_date_desc', 'stock_id', date.desc()),
    )

class SuppressionScore(Base):
    __tablename__ = "suppression_scores"
    
    id = Column(Integer, primary_key=True, index=True)
    stock_id = Column(Integer, ForeignKey("stocks.id"), index=True)
    ma_period = Column(Integer, index=True)  # e.g., 20 for MA20
    score = Column(Float, index=True)  # Index for sorting by score
    contacts = Column(Integer)  # Number of contacts with MA
    breakthroughs = Column(Integer)  # Number of breakthroughs
    avg_deviation = Column(Float)  # Average deviation from MA
    stock = relationship("Stock", back_populates="suppression_scores")
    
    __table_args__ = (
        # Composite index for efficient filtering and sorting
        Index('idx_stock_score', 'stock_id', 'score'),
        # Index for finding best MA period
        Index('idx_stock_ma', 'stock_id', 'ma_period'),
        # Index for score sorting with stock info
        Index('idx_score_stock', 'score', 'stock_id', 'ma_period'),
    )
