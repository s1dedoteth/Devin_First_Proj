import os
from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import create_engine, text, func, desc
from sqlalchemy.orm import sessionmaker, Session
from .models import Base, Stock, StockPrice, SuppressionScore
from .services.stock_service import StockService
from .services.suppression_service import SuppressionService
from .services.scheduler import setup_scheduler
from functools import lru_cache
from typing import Dict, Any, Optional, Tuple, List
import json
import time
from datetime import datetime, timedelta

# Use SQLite for development
SQLALCHEMY_DATABASE_URL = "sqlite:///./ma_suppression.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create all tables
Base.metadata.create_all(bind=engine)

app = FastAPI()

# Initialize scheduler on startup
@app.on_event("startup")
async def startup_event():
    """Initialize scheduler and populate database if empty."""
    db = SessionLocal()
    try:
        # Check if database is empty
        stock_count = db.query(Stock).count()
        if stock_count == 0:
            print("Database is empty. Fetching real stock data...")
            stock_service = StockService(db)
            
            # Fetch real stock data
            try:
                print("Fetching stock symbols...")
                stocks = stock_service.fetch_index_constituents()
                print(f"Found {len(stocks)} stocks. Fetching details...")
                
                for stock_info in stocks:
                    try:
                        details = stock_service.get_stock_info(
                            stock_info['symbol'],
                            stock_info['index_type']
                        )
                        if details:
                            stock = Stock(**details)
                            db.add(stock)
                            db.commit()
                            print(f"Added {stock.symbol}")
                    except Exception as e:
                        print(f"Error adding {stock_info['symbol']}: {e}")
                        continue
                
                print("Stock data fetching complete.")
                
                # Initialize suppression analysis
                suppression_service = SuppressionService(db)
                suppression_service.analyze_all_stocks()
                print("Suppression analysis complete.")
            except Exception as e:
                print(f"Error during stock data fetching: {e}")
                
                # Fallback to test data if real data fetching fails
                if os.getenv('ALLOW_TEST_DATA', '').lower() == 'true':
                    print("Falling back to test data...")
                    from tests.test_pagination import create_test_data
                    create_test_data(db)
                    print("Test data generation complete.")
                    
                    suppression_service = SuppressionService(db)
                    suppression_service.analyze_all_stocks()
                    print("Suppression analysis complete.")
        
        # Set up scheduler for daily updates
        setup_scheduler(db)
    except Exception as e:
        print(f"Error during startup: {e}")
    finally:
        db.close()

# Configure CORS for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:4173",
        "http://localhost:5173",
        "http://localhost:3000"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"]
)

# Dependency for database sessions
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.get("/healthz")
async def healthz(db: Session = Depends(get_db)):
    try:
        # Test database connection
        db.execute(text("SELECT 1"))
        return {"status": "ok", "database": "connected"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database connection failed: {str(e)}")

@app.post("/api/stocks/update")
async def update_stocks(db: Session = Depends(get_db)):
    """Manually trigger stock data update."""
    try:
        stock_service = StockService(db)
        stock_service.update_all_data()
        
        # After updating stock data, analyze suppression patterns
        suppression_service = SuppressionService(db)
        suppression_service.analyze_all_stocks()
        
        return {
            "status": "success", 
            "message": "Stock data and suppression analysis completed"
        }
    except Exception as e:
        raise HTTPException(
            status_code=500, 
            detail=f"Failed to update stock data: {str(e)}"
        )

from typing import Optional
from sqlalchemy import desc, func
import time

@app.get("/api/stocks/{symbol}/historical")
async def get_historical_data(
    symbol: str,
    days: int = 30,
    db: Session = Depends(get_db)
):
    """Get historical price data and moving average for a stock."""
    try:
        # Get the stock
        stock = db.query(Stock).filter(Stock.symbol == symbol).first()
        if not stock:
            raise HTTPException(status_code=404, detail="Stock not found")
            
        # Get the best MA period for this stock first
        best_ma = (
            db.query(SuppressionScore)
            .filter(SuppressionScore.stock_id == stock.id)
            .order_by(SuppressionScore.score.desc())
            .first()
        )
        
        if not best_ma:
            raise HTTPException(status_code=404, detail="No MA data found")
            
        # Get historical prices with pre-calculated MA using window function
        required_days = days + best_ma.ma_period  # Extra days for MA calculation
        cache_key = f"{symbol}_{days}_{best_ma.ma_period}"
        
        @lru_cache(maxsize=1000)
        def get_cached_prices(key: str) -> List[Dict]:
            symbol, days_str, period = key.split('_')
            days_needed = int(days_str) + int(period)
            
            # Use raw SQL for moving average calculation
            ma_sql = text(f"""
                WITH numbered_prices AS (
                    SELECT date, close,
                           ROW_NUMBER() OVER (ORDER BY date DESC) as row_num
                    FROM stock_prices
                    WHERE stock_id = :stock_id
                ),
                prices_with_ma AS (
                    SELECT p1.date, p1.close,
                           AVG(p2.close) as ma
                    FROM numbered_prices p1
                    LEFT JOIN numbered_prices p2
                    ON p2.date <= p1.date
                    AND p2.date > date(p1.date, '-{best_ma.ma_period} days')
                    WHERE p1.row_num <= :days_needed
                    GROUP BY p1.date, p1.close
                )
                SELECT date, close, ROUND(ma, 4) as ma
                FROM prices_with_ma
                ORDER BY date DESC
            """)
            
            prices_with_ma = db.execute(
                ma_sql,
                {"stock_id": stock.id, "days_needed": days_needed}
            ).all()
            
            return [
                {
                    'date': price.date,
                    'price': price.close,
                    'ma': round(price.ma, 4) if price.ma is not None else None
                }
                for price in prices_with_ma
            ]
            
        price_data = list(reversed(get_cached_prices(cache_key)))
        
        # Format dates as ISO strings
        for point in price_data:
            point['date'] = point['date'].isoformat()
            
        return price_data
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

def get_cache_key(
    search: Optional[str],
    sort: Optional[str],
    order: Optional[str],
    page: int,
    limit: int,
    index_type: Optional[str] = None
) -> str:
    """Generate a cache key from query parameters."""
    params = {
        "search": search or "",
        "sort": sort or "score",
        "order": order or "desc",
        "page": max(page, 1),
        "limit": max(limit, 1),
        "index_type": index_type or ""
    }
    return json.dumps(params, sort_keys=True)

from contextlib import contextmanager

@contextmanager
def get_db_session():
    """Get database session with proper cleanup."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@lru_cache(maxsize=256)
def get_cached_stocks(params_str: str) -> Dict[str, Any]:
    """Get cached stock data using string parameters as cache key."""
    params = json.loads(params_str)
    with get_db_session() as db:
        return execute_stock_query(params, db)

def execute_stock_query(params: dict, db: Session) -> Dict:
    """Execute the stock query with given parameters and return formatted response."""
    # Get latest prices first
    latest_prices = (
        db.query(
            StockPrice.stock_id,
            StockPrice.date,
            StockPrice.close,
            func.row_number().over(
                partition_by=StockPrice.stock_id,
                order_by=StockPrice.date.desc()
            ).label('rn')
        )
        .subquery()
    )
    
    # Get best suppression scores with COALESCE to handle NULLs
    best_scores = (
        db.query(
            SuppressionScore.stock_id,
            func.coalesce(SuppressionScore.ma_period, 20).label('ma_period'),
            func.coalesce(SuppressionScore.score, 0.0).label('score'),
            func.row_number().over(
                partition_by=SuppressionScore.stock_id,
                order_by=func.coalesce(SuppressionScore.score, 0.0).desc()
            ).label('rn')
        )
        .subquery()
    )
    
    # Build main query with efficient joins
    query = (
        db.query(
            Stock,
            best_scores.c.ma_period,
            best_scores.c.score,
            latest_prices.c.close,
            latest_prices.c.date
        )
        .outerjoin(best_scores, (Stock.id == best_scores.c.stock_id) & (best_scores.c.rn == 1))
        .outerjoin(latest_prices, (Stock.id == latest_prices.c.stock_id) & (latest_prices.c.rn == 1))
    )
    
    # Apply search filter if provided
    if params["search"]:
        search = f"%{params['search']}%"
        query = query.filter(
            (Stock.symbol.ilike(search)) |
            (Stock.name.ilike(search))
        )
    
    # Apply index type filter if provided
    if params["index_type"]:
        query = query.filter(Stock.index_type == params["index_type"])
    
    # Apply sorting
    if params["sort"] == "score":
        query = query.order_by(
            desc(best_scores.c.score) if params["order"] == "desc"
            else best_scores.c.score
        )
    elif params["sort"] == "ma_period":
        query = query.order_by(
            desc(best_scores.c.ma_period) if params["order"] == "desc"
            else best_scores.c.ma_period
        )
    else:
        # Default sort by market cap
        query = query.order_by(desc(Stock.market_cap))
    
    # Get total count directly from stocks table with filters
    count_query = db.query(Stock)
    if params["search"]:
        count_query = count_query.filter(
            (Stock.symbol.ilike(f"%{params['search']}%")) |
            (Stock.name.ilike(f"%{params['search']}%"))
        )
    if params["index_type"]:
        count_query = count_query.filter(Stock.index_type == params["index_type"])
    total_count = count_query.count()
    
    # Apply pagination
    page = max(params["page"], 1)
    limit = max(params["limit"], 1)
    offset = (page - 1) * limit
    query = query.offset(offset).limit(limit)
    
    # Execute query and format results
    stocks = []
    for stock, ma_period, score, latest_price, latest_date in query.all():
        # Handle NULL values
        ma_period = ma_period or 20  # Default to MA20 if NULL
        score = score or 0.0  # Default to 0.0 if NULL
        latest_price = latest_price or 0.0  # Default to 0.0 if NULL
        
        stocks.append({
            "symbol": stock.symbol,
            "name": stock.name,
            "market_cap": stock.market_cap,
            "index_type": stock.index_type,
            "best_ma": f"MA{ma_period}",
            "suppression_score": round(float(score), 4),
            "latest_price": float(latest_price),
            "latest_date": latest_date.isoformat() if latest_date else None
        })
    
    return {
        "stocks": stocks,
        "total": total_count,
        "page": params["page"],
        "limit": params["limit"],
        "total_pages": (total_count + params["limit"] - 1) // params["limit"]
    }

@app.get("/api/stocks")
async def get_stocks(
    db: Session = Depends(get_db),
    search: Optional[str] = None,
    sort: Optional[str] = "score",  # Default sort by score
    order: Optional[str] = "desc",
    page: int = 1,
    limit: int = 50,  # Default 50 stocks per page
    index_type: Optional[str] = None
):
    """
    Get list of stocks with their best moving averages and suppression scores.
    
    Args:
        search: Optional search term for stock symbol or name
        sort: Sort field ('score' or 'ma_period')
        order: Sort order ('asc' or 'desc')
        index_type: Filter by index type ('RUSSELL2000' or 'NASDAQ')
    """
    try:
        # Prepare query parameters
        params = {
            "search": search or "",
            "sort": sort or "score",
            "order": order or "desc",
            "page": max(page, 1),
            "limit": max(limit, 1),
            "index_type": index_type or ""
        }
        
        # Convert params to string for cache key
        params_str = json.dumps(params, sort_keys=True)
        
        # Get data from cache or compute it
        query_start = time.time()
        result = get_cached_stocks(params_str)
        stocks = result.get("stocks", [])
        total_count = result.get("total", 0)
        query_time = time.time() - query_start
        cache_info = get_cached_stocks.cache_info()
        print(f"Query took {query_time:.2f}s for {len(stocks)} stocks (hits={cache_info.hits}, misses={cache_info.misses}, size={cache_info.currsize})")
        
        # Return paginated response
        return {
            "stocks": stocks,
            "total": total_count,
            "page": page,
            "limit": limit,
            "total_pages": (total_count + limit - 1) // limit
        }
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to fetch stocks: {str(e)}"
        )
