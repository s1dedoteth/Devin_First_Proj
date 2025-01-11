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
    
    # Generate test stocks (50 NASDAQ, 50 Russell 2000 for memory efficiency)
    stocks = []
    
    # NASDAQ stocks
    for i in range(50):
        symbol = f"NSDQ{i:04d}"
        stock = Stock(
            symbol=symbol,
            name=f"NASDAQ Stock {i}",
            market_cap=random.uniform(1e9, 500e9),  # 1B to 500B
            index_type="NASDAQ"
        )
        stocks.append(stock)
    
    # Russell 2000 stocks
    for i in range(50):
        symbol = f"RUSS{i:04d}"
        stock = Stock(
            symbol=symbol,
            name=f"Russell Stock {i}",
            market_cap=random.uniform(0.5e9, 10e9),  # 500M to 10B
            index_type="RUSSELL2000"
        )
        stocks.append(stock)
    
    # Add stocks to database in smaller batches
    batch_size = 10
    for i in range(0, len(stocks), batch_size):
        batch = stocks[i:i+batch_size]
        db.add_all(batch)
        db.commit()
        print(f"Added stocks {i+1}-{i+len(batch)}")
    
    # Generate price data with batch processing (1 year of data is enough for MA60)
    # Use explicit historical dates to avoid future dates
    end_date = datetime(2023, 12, 31)  # End at last year
    start_date = end_date - timedelta(days=365)  # 1 year of data
    dates = [start_date + timedelta(days=x) for x in range(365) if (start_date + timedelta(days=x)) <= end_date]
    
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
    ma_periods = [10, 20, 30, 40, 50, 60]  # Limited to MA10-MA60 range
    batch_size = 5  # Process 5 stocks at a time to reduce memory usage
    
    for batch_start in range(0, total_stocks, batch_size):
        try:
            batch_end = min(batch_start + batch_size, total_stocks)
            stock_batch = stocks[batch_start:batch_end]
            scores = []
            
            for stock in stock_batch:
                for period in ma_periods:
                    # Generate realistic scores based on MA period
                    # Shorter periods tend to have more contacts and breakthroughs
                    contacts = max(5, int(30 * (1 - period/60)))  # More contacts for shorter periods
                    breakthroughs = max(2, int(15 * (1 - period/60)))  # More breakthroughs for shorter periods
                    avg_deviation = random.uniform(0.5, 2.0) * (period/10)  # Higher deviation for longer periods
                    
                    score = SuppressionScore(
                        stock_id=stock.id,
                        ma_period=period,
                        score=random.uniform(-0.3, 0.3),  # More conservative score range
                        contacts=contacts,
                        breakthroughs=breakthroughs,
                        avg_deviation=avg_deviation
                    )
                    scores.append(score)
            
            # Bulk insert scores for this batch
            db.add_all(scores)
            db.commit()
            print(f"Progress: {batch_end}/{total_stocks} stocks processed ({len(scores)} scores)")
            
        except Exception as e:
            print(f"Error processing batch {batch_start}-{batch_end}: {e}")
            continue  # Continue with next batch on error
    
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
        base_url = "https://app-vicjccoq.fly.dev/api/stocks"
        max_retries = 3
        retry_delay = 5  # seconds
        
        print("\nTesting pagination performance...")
        print(f"Using deployed URL: {base_url}")
        
        # Test different page sizes with retries
        for limit in [10, 50, 100]:
            for attempt in range(max_retries):
                start_time = time.time()
                try:
                    response = requests.get(
                        f"{base_url}?page=1&limit={limit}",
                        timeout=10  # Add timeout
                    )
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
                    
                    # Success, break retry loop
                    break
                    
                except Exception as e:
                    print(f"Attempt {attempt + 1}/{max_retries} failed: {e}")
                    if attempt < max_retries - 1:
                        print(f"Retrying in {retry_delay} seconds...")
                        time.sleep(retry_delay)
                    else:
                        print("All retries failed")
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

def verify_ma_constraints():
    """Verify that all MA periods are within the allowed range [10-60]."""
    db = SessionLocal()
    try:
        # Check all MA periods in database
        scores = db.query(SuppressionScore.ma_period).distinct().all()
        ma_periods = [score[0] for score in scores]
        for period in ma_periods:
            assert 10 <= period <= 60, f"Found MA period {period} outside allowed range [10-60]"
        print(f"\nVerified {len(ma_periods)} unique MA periods, all within [10-60] range")
        
        # Check MA periods in API response
        response = requests.get("http://localhost:8000/api/stocks?limit=50")
        data = response.json()
        for stock in data.get('stocks', []):
            ma_period = int(stock['best_ma'].replace('MA', ''))
            assert 10 <= ma_period <= 60, f"API returned MA period {ma_period} outside allowed range [10-60]"
        print("Verified all API response MA periods are within [10-60] range")
        
    finally:
        db.close()

if __name__ == "__main__":
    test_pagination()
    verify_ma_constraints()
