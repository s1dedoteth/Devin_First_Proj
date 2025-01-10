import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.services.stock_service import StockService
from sqlalchemy.orm import Session
from sqlalchemy import create_engine
from app.models import Base

# Create test database engine
engine = create_engine("sqlite:///./test.db", connect_args={"check_same_thread": False})

# Create tables
Base.metadata.create_all(bind=engine)

# Create session
session = Session(engine)

# Initialize service
service = StockService(session)

# Test NASDAQ fetching
print("\nFetching NASDAQ symbols...")
nasdaq_symbols = service.fetch_full_nasdaq_symbols()
print(f"Found {len(nasdaq_symbols)} NASDAQ symbols")
print("Sample NASDAQ symbols:", nasdaq_symbols[:5] if nasdaq_symbols else "None")

# Test Russell 2000 fetching
print("\nFetching Russell 2000 symbols...")
russell_symbols = service.fetch_full_russell_symbols()
print(f"Found {len(russell_symbols)} Russell 2000 symbols")
print("Sample Russell symbols:", russell_symbols[:5] if russell_symbols else "None")

# Test combined fetching
print("\nFetching all stocks...")
all_stocks = service.fetch_index_constituents()
print(f"Found {len(all_stocks)} total stocks")
print("Sample stocks:", all_stocks[:5] if all_stocks else "None")
