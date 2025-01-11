from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import create_engine, text, func, desc
from sqlalchemy.orm import sessionmaker, Session
from .models import Base, Stock, StockPrice, SuppressionScore
from .services.stock_service import StockService
from .services.suppression_service import SuppressionService
from .services.scheduler import setup_scheduler
from functools import lru_cache
from typing import Dict, Any, Optional, Tuple
import json
import time

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
            print("Database is empty. Generating test data...")
            from test_pagination import create_test_data
            create_test_data(db)
            print("Test data generation complete.")
            
            # Initialize suppression analysis
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
            
        # Get historical prices for the specified days (fetch extra for MA calculation)
        required_days = days + best_ma.ma_period  # Extra days for MA calculation
        prices = (
            db.query(StockPrice)
            .filter(StockPrice.stock_id == stock.id)
            .order_by(StockPrice.date.desc())
            .limit(required_days)
            .all()
        )
        
        if not best_ma:
            raise HTTPException(status_code=404, detail="No MA data found")
            
        # Calculate moving average
        price_data = []
        ma_period = best_ma.ma_period
        prices = list(reversed(prices))  # Reverse to get chronological order
        
        for i, price in enumerate(prices):
            data_point = {
                "date": price.date.isoformat(),
                "price": price.close,
                "ma": None
            }
            
            # Calculate MA if we have enough previous data points
            if i >= ma_period - 1:
                ma_sum = sum(p.close for p in prices[i - ma_period + 1:i + 1])
                data_point["ma"] = round(ma_sum / ma_period, 4)
                
            price_data.append(data_point)
            
        return price_data
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

def get_cache_key(search: Optional[str], sort: Optional[str], order: Optional[str], page: int, limit: int) -> str:
    """Generate a cache key from query parameters."""
    params = {
        "search": search,
        "sort": sort,
        "order": order,
        "page": page,
        "limit": limit
    }
    return json.dumps(params, sort_keys=True)

@lru_cache(maxsize=256)
def get_cached_stocks(cache_key: str, db: Session) -> Tuple[list, int]:
    """Cached function to get stocks data."""
    # Parse cache key back into parameters
    params = json.loads(cache_key)
    
    # Start with base query
    query = db.query(
        Stock,
        SuppressionScore.ma_period,
        SuppressionScore.score,
        StockPrice.close,
        StockPrice.date
    )
    
    # Join with suppression scores and get the highest score for each stock
    subq = (
        db.query(
            SuppressionScore.stock_id,
            func.max(SuppressionScore.score).label('max_score')
        )
        .group_by(SuppressionScore.stock_id)
        .subquery()
    )
    
    query = query.join(subq, Stock.id == subq.c.stock_id)
    query = query.join(
        SuppressionScore,
        (SuppressionScore.stock_id == Stock.id) & 
        (SuppressionScore.score == subq.c.max_score)
    )
    
    # Get latest price
    latest_prices = (
        db.query(
            StockPrice.stock_id,
            func.max(StockPrice.date).label('max_date')
        )
        .group_by(StockPrice.stock_id)
        .subquery()
    )
    
    query = query.join(
        latest_prices,
        Stock.id == latest_prices.c.stock_id
    )
    query = query.join(
        StockPrice,
        (StockPrice.stock_id == Stock.id) &
        (StockPrice.date == latest_prices.c.max_date)
    )
    
    # Apply search filter if provided
    if params["search"]:
        search = f"%{params['search']}%"
        query = query.filter(
            (Stock.symbol.ilike(search)) |
            (Stock.name.ilike(search))
        )
    
    # Apply sorting
    if params["sort"] == "score":
        query = query.order_by(
            desc(SuppressionScore.score) if params["order"] == "desc"
            else SuppressionScore.score
        )
    elif params["sort"] == "ma_period":
        query = query.order_by(
            desc(SuppressionScore.ma_period) if params["order"] == "desc"
            else SuppressionScore.ma_period
        )
    else:
        # Default sort by market cap
        query = query.order_by(desc(Stock.market_cap))
    
    # Get total count
    total_count = query.count()
    
    # Apply pagination
    page = max(params["page"], 1)
    limit = max(params["limit"], 1)
    offset = (page - 1) * limit
    query = query.offset(offset).limit(limit)
    
    # Execute query and format results
    stocks = []
    for stock, ma_period, score, latest_price, latest_date in query.all():
        stocks.append({
            "symbol": stock.symbol,
            "name": stock.name,
            "market_cap": stock.market_cap,
            "index_type": stock.index_type,
            "best_ma": f"MA{ma_period}",
            "suppression_score": round(score, 4),
            "latest_price": latest_price,
            "latest_date": latest_date
        })
    
    return stocks, total_count

@app.get("/api/stocks")
async def get_stocks(
    db: Session = Depends(get_db),
    search: Optional[str] = None,
    sort: Optional[str] = "score",  # Default sort by score
    order: Optional[str] = "desc",
    page: int = 1,
    limit: int = 50  # Default 50 stocks per page
):
    """
    Get list of stocks with their best moving averages and suppression scores.
    
    Args:
        search: Optional search term for stock symbol or name
        sort: Sort field ('score' or 'ma_period')
        order: Sort order ('asc' or 'desc')
    """
    try:
        # Generate cache key from query parameters
        cache_key = get_cache_key(search, sort, order, page, limit)
        
        # Get data from cache or compute it
        query_start = time.time()
        stocks, total_count = get_cached_stocks(cache_key, db)
        query_time = time.time() - query_start
        print(f"Query took {query_time:.2f}s for {len(stocks)} stocks (cached={get_cached_stocks.cache_info().hits}/{get_cached_stocks.cache_info().misses})")
        
        # Return paginated response
        return {
            "stocks": stocks,
            "total": total_count,
            "page": page,
            "limit": limit,
            "total_pages": (total_count + limit - 1) // limit
        }
        
        return {
            "stocks": result,
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
