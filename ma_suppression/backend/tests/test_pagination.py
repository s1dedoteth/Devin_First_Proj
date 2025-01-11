import sys
import os
import random
from datetime import datetime, timedelta
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.main import engine, SessionLocal
from app.models import Base, Stock, StockPrice, SuppressionScore
from sqlalchemy import create_engine
import requests
import time
import json

def create_test_data(db):
    """Create synthetic test data."""
    print("\nCreating test data...")
    
    # Generate test stocks (1000 NASDAQ, 2000 Russell 2000)
    stocks = []
    
    # NASDAQ stocks
    for i in range(1000):
        symbol = f"NSDQ{i:04d}"
        stock = Stock(
            symbol=symbol,
            name=f"NASDAQ Stock {i}",
            market_cap=random.uniform(1e9, 500e9),  # 1B to 500B
            index_type="NASDAQ"
        )
        stocks.append(stock)
    
    # Russell 2000 stocks
    for i in range(2000):
        symbol = f"RUSS{i:04d}"
        stock = Stock(
            symbol=symbol,
            name=f"Russell Stock {i}",
            market_cap=random.uniform(0.5e9, 10e9),  # 500M to 10B
            index_type="RUSSELL2000"
        )
        stocks.append(stock)
    
    # Add stocks to database
    db.add_all(stocks)
    db.commit()
    
    # Generate price data with batch processing (2 years for MA200)
    end_date = datetime.now()
    start_date = end_date - timedelta(days=730)  # 2 years
    dates = [start_date + timedelta(days=x) for x in range(730)]
    
    print("\nGenerating price data...")
    total_stocks = len(stocks)
    batch_size = 50  # Process 50 stocks at a time
    
    for batch_start in range(0, total_stocks, batch_size):
        batch_end = min(batch_start + batch_size, total_stocks)
        stock_batch = stocks[batch_start:batch_end]
        all_prices = []
        
        for stock in stock_batch:
            base_price = random.uniform(10, 1000)
            current_price = base_price
            
            for date in dates:
                # Generate realistic price movement
                daily_change = random.uniform(-0.03, 0.03)
                current_price *= (1 + daily_change)
                
                all_prices.append(
                    StockPrice(
                        stock_id=stock.id,
                        date=date,
                        open=current_price * (1 + random.uniform(-0.01, 0.01)),
                        high=current_price * (1 + random.uniform(0, 0.02)),
                        low=current_price * (1 - random.uniform(0, 0.02)),
                        close=current_price
                    )
                )
        
        # Bulk insert all prices for this batch
        db.add_all(all_prices)
        db.commit()
        print(f"Progress: {batch_end}/{total_stocks} stocks processed ({len(all_prices)} price points)")
    
    print("\nGenerating suppression scores...")
    ma_periods = [5, 10, 20, 50, 100, 200]
    batch_size = 100  # Process 100 stocks at a time
    
    for batch_start in range(0, total_stocks, batch_size):
        batch_end = min(batch_start + batch_size, total_stocks)
        stock_batch = stocks[batch_start:batch_end]
        scores = []
        
        for stock in stock_batch:
            for period in ma_periods:
                score = SuppressionScore(
                    stock_id=stock.id,
                    ma_period=period,
                    score=random.uniform(-0.5, 0.5),
                    contacts=random.randint(10, 100),
                    breakthroughs=random.randint(5, 30),
                    avg_deviation=random.uniform(0.5, 5.0)
                )
                scores.append(score)
        
        # Bulk insert scores for this batch
        db.add_all(scores)
        db.commit()
        print(f"Progress: {batch_end}/{total_stocks} stocks processed ({len(scores)} scores)")
    
    print("Test data creation complete.")

def test_pagination():
    """Test pagination performance with synthetic data."""
    db = SessionLocal()
    try:
        # Check if data exists
        stock_count = db.query(Stock).count()
        if stock_count == 0:
            print("\nInitializing database...")
            Base.metadata.create_all(bind=engine)
            create_test_data(db)
        else:
            print(f"\nUsing existing data ({stock_count} stocks)")
            
        # Ensure suppression scores are calculated
        from app.services.suppression_service import SuppressionService
        print("\nCalculating suppression scores...")
        suppression_service = SuppressionService(db)
        suppression_service.analyze_all_stocks()
        print("Suppression analysis complete.")
        
        # Test pagination endpoints
        base_url = "http://localhost:8000/api/stocks"
        
        print("\nTesting pagination performance...")
        
        # Test different page sizes
        for limit in [10, 50, 100]:
            start_time = time.time()
            try:
                response = requests.get(f"{base_url}?page=1&limit={limit}")
                response.raise_for_status()
                data = response.json()
                duration = time.time() - start_time
                
                print(f"\nPage size {limit}:")
                print(f"- Total stocks: {data.get('total', 0)}")
                print(f"- Total pages: {data.get('total_pages', 0)}")
                print(f"- Response time: {duration:.2f}s")
                print(f"- Stocks per page: {len(data.get('stocks', []))}")
                
                if duration > 2.0:
                    print(f"WARNING: Response time exceeds 2 seconds target")
                    
            except Exception as e:
                print(f"Error testing page size {limit}: {e}")
                print(f"Response content: {response.text if 'response' in locals() else 'No response'}")
                continue
        
        # Test with search filter
        print("\nTesting search performance...")
        start_time = time.time()
        response = requests.get(f"{base_url}?page=1&limit=50&search=NSDQ")
        data = response.json()
        duration = time.time() - start_time
        print(f"Search 'NSDQ' results: {len(data['stocks'])} stocks")
        print(f"Search response time: {duration:.2f}s")
        
        # Test sorting
        print("\nTesting sorting performance...")
        for sort in ['score', 'ma_period']:
            for order in ['asc', 'desc']:
                start_time = time.time()
                response = requests.get(f"{base_url}?page=1&limit=50&sort={sort}&order={order}")
                duration = time.time() - start_time
                print(f"Sort by {sort} {order}: {duration:.2f}s")
        
        # Test index filtering
        print("\nTesting index filtering...")
        for index in ['NASDAQ', 'RUSSELL2000']:
            start_time = time.time()
            response = requests.get(f"{base_url}?page=1&limit=50&index_type={index}")
            data = response.json()
            duration = time.time() - start_time
            print(f"Filter by {index}: {len(data['stocks'])} stocks, {duration:.2f}s")
            if duration > 2.0:
                print(f"WARNING: Index filtering response time exceeds 2 seconds target")

        # Test chart loading performance
        print("\nTesting chart loading performance...")
        test_symbols = ['NSDQ0000', 'RUSS0000']  # Test first stock from each index
        for symbol in test_symbols:
            for days in [30, 60, 100, 200]:
                start_time = time.time()
                response = requests.get(f"{base_url}/{symbol}/historical?days={days}")
                data = response.json()
                duration = time.time() - start_time
                print(f"Chart data for {symbol} ({days} days): {duration:.2f}s")
                if duration > 2.0:
                    print(f"WARNING: Chart loading response time exceeds 2 seconds target")
                    
        # Print performance summary
        print("\nPerformance Summary:")
        print("Response times should be under 2 seconds for optimal user experience")
        print("- List loading (50 stocks per page)")
        print("- Chart loading (up to 200 days)")
        
    finally:
        db.close()

if __name__ == "__main__":
    test_pagination()
