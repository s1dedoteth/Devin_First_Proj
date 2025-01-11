import sys
import os
import pytest
import asyncio
from sqlalchemy.orm import Session
from sqlalchemy import create_engine

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from app.services.stock_service import StockService
from app.models import Base

# Test database setup
@pytest.fixture(scope="module")
def engine():
    return create_engine("sqlite:///./test.db")

@pytest.fixture(scope="module")
def db_session(engine):
    Base.metadata.create_all(bind=engine)
    session = Session(engine)
    yield session
    session.close()

@pytest.fixture(scope="module")
def stock_service(db_session):
    return StockService(db_session)

@pytest.mark.asyncio
async def test_nasdaq_fetching(stock_service):
    """Test NASDAQ stock fetching."""
    print("\nFetching NASDAQ symbols...")
    nasdaq_symbols = await stock_service.fetch_full_nasdaq_symbols()
    assert len(nasdaq_symbols) > 0, "No NASDAQ symbols found"
    print(f"Found {len(nasdaq_symbols)} NASDAQ symbols")
    print("Sample NASDAQ symbols:", nasdaq_symbols[:5])

@pytest.mark.asyncio
async def test_russell_fetching(stock_service):
    """Test Russell 2000 stock fetching."""
    print("\nFetching Russell 2000 symbols...")
    russell_symbols = await stock_service.fetch_full_russell_symbols()
    assert len(russell_symbols) > 0, "No Russell 2000 symbols found"
    print(f"Found {len(russell_symbols)} Russell 2000 symbols")
    print("Sample Russell symbols:", russell_symbols[:5])

@pytest.mark.asyncio
async def test_combined_fetching(stock_service):
    """Test combined stock fetching."""
    print("\nFetching all stocks...")
    all_stocks = await stock_service.fetch_index_constituents()
    assert len(all_stocks) > 0, "No stocks found"
    print(f"Found {len(all_stocks)} total stocks")
    print("Sample stocks:", all_stocks[:5])
