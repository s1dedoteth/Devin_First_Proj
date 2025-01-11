import os
import gc
import json
import time
import asyncio
import importlib
from datetime import datetime, timedelta
from typing import Dict, Any, Optional, Tuple, List
from functools import lru_cache
from contextlib import asynccontextmanager

# Core imports that are always needed
from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker, Session

# Force garbage collection on import
gc.collect()

# Lazy imports
def import_models():
    """Import models only when needed."""
    from .models import Base, Stock, StockPrice, SuppressionScore
    return Base, Stock, StockPrice, SuppressionScore

def import_services():
    """Import services only when needed."""
    from .services.stock_service import StockService
    from .services.suppression_service import SuppressionService
    from .services.scheduler import setup_scheduler
    return StockService, SuppressionService, setup_scheduler

# Import models and services at module level but with minimal initial footprint
from .models import Base, Stock, StockPrice, SuppressionScore
from .services.stock_service import StockService
from .services.suppression_service import SuppressionService
from .services.scheduler import setup_scheduler

# Defer heavy initialization until needed
def init_models():
    """Initialize database models."""
    Base.metadata.create_all(bind=engine)

def init_services(db):
    """Initialize services with database session."""
    return StockService(db), SuppressionService(db), setup_scheduler

# Use SQLite with proper path
DB_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data")
os.makedirs(DB_DIR, exist_ok=True)
DB_PATH = os.path.join(DB_DIR, "ma_suppression.db")
# Configure SQLite to use WAL mode for better concurrency and performance
import sqlite3
def setup_sqlite_wal():
    """Configure SQLite connection to use WAL mode."""
    conn = sqlite3.connect(DB_PATH)
    conn.execute('PRAGMA journal_mode=WAL')
    conn.execute('PRAGMA synchronous=NORMAL')
    conn.execute('PRAGMA cache_size=-64000')  # 64MB cache
    conn.execute('PRAGMA mmap_size=17179869184')  # 16GB mmap
    conn.close()

setup_sqlite_wal()

SQLALCHEMY_DATABASE_URL = f"sqlite:///{DB_PATH}"
engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={
        "check_same_thread": False,
        "timeout": 30,
        "isolation_level": "READ UNCOMMITTED"
    },
    # Aggressive connection pooling
    pool_size=1,
    max_overflow=0,
    pool_timeout=30,
    pool_recycle=1800
)
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
    expire_on_commit=False  # Prevent unnecessary reloads
)

# Defer table creation until after server startup
# Base.metadata.create_all(bind=engine)

app = FastAPI()

# Initialize scheduler on startup
import gc
import asyncio
from contextlib import asynccontextmanager

# Global initialization flag
is_initializing = False
initialization_progress = {"stocks": 0, "scores": 0}

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan context manager for FastAPI app."""
    # Startup
    print("Starting application...")
    yield
    # Shutdown
    print("Shutting down application...")

app = FastAPI(lifespan=lifespan)

async def init_database():
    """Initialize database asynchronously with minimal memory usage."""
    global is_initializing, initialization_progress
    
    if is_initializing:
        return
        
    is_initializing = True
    
    try:
        # Initialize models only when needed
        init_models()
        
        # Force garbage collection after initialization
        gc.collect()
        
        db = SessionLocal()
        try:
            # Check database status
            stock_count = db.query(Stock).count()
            scores_count = db.query(SuppressionScore).count()
            print(f"\nDatabase status: {stock_count} stocks, {scores_count} scores")
            
            # Initialize database if empty
            if stock_count == 0:
                print("\nInitializing database with minimal test data...")
                
                # Import test data module only when needed
                from tests.test_pagination import create_test_data
                
                # Process in very small batches
                batch_size = 2  # Reduced batch size for lower memory usage
                try:
                    create_test_data(db, batch_size=batch_size)
                    print("Test data created successfully")
                    await asyncio.sleep(1)
                    gc.collect()  # Force garbage collection after data creation
                except Exception as e:
                    print(f"Error creating test data: {e}")
                    return
                
                # Update progress
                stock_count = db.query(Stock).count()
                initialization_progress["stocks"] = stock_count
                
                # Calculate scores in minimal batches
                print("\nCalculating suppression scores...")
                suppression_service = SuppressionService(db)
                
                # Process stocks in chunks to minimize memory usage
                offset = 0
                while True:
                    # Get a small batch of stocks
                    stocks = db.query(Stock).offset(offset).limit(batch_size).all()
                    if not stocks:
                        break
                        
                    for stock in stocks:
                        for period in suppression_service.ma_periods:
                            try:
                                result = suppression_service.analyze_stock(stock, period)
                                if result:
                                    score = SuppressionScore(
                                        stock_id=stock.id,
                                        ma_period=int(period),
                                        score=float(result['score']),
                                        contacts=int(result['contacts']),
                                        breakthroughs=int(result['breakthroughs']),
                                        avg_deviation=float(result['avg_deviation'])
                                    )
                                    db.add(score)
                            except Exception as e:
                                print(f"Error analyzing {stock.symbol} MA{period}: {e}")
                                continue
                        
                        # Commit after each stock to minimize memory usage
                        db.commit()
                        scores_count = db.query(SuppressionScore).count()
                        initialization_progress["scores"] = scores_count
                        
                        # Force garbage collection and yield
                        gc.collect()
                        await asyncio.sleep(0.1)
                    
                    offset += batch_size
                    print(f"Progress: {offset} stocks processed, {scores_count} scores calculated")
            
            # Set up scheduler with minimal configuration
            setup_scheduler(db)
            print("Scheduler initialized")
            
        finally:
            db.close()
            
    except Exception as e:
        print(f"Error during initialization: {e}")
    finally:
        is_initializing = False
        gc.collect()  # Final garbage collection

@app.on_event("startup")
async def startup_event():
    """Start database initialization in background after server is up."""
    # Delay database initialization to allow server to start with minimal memory
    async def delayed_init():
        await asyncio.sleep(5)  # Give server time to stabilize
        await init_database()
    
    # Create background task
    asyncio.create_task(delayed_init())

# Configure CORS for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://localhost:4173",
        "https://moving-average-analysis-app-k51ft6e1.devinapps.com"
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
        
        # Check initialization status
        stock_count = db.query(Stock).count()
        scores_count = db.query(SuppressionScore).count()
        
        # Calculate expected counts
        expected_stocks = 10  # Minimal test data size (5 NASDAQ + 5 Russell)
        expected_scores = expected_stocks * len(SuppressionService(db).ma_periods)
        
        # Check if both stocks and scores are fully populated
        initialization_complete = (
            stock_count >= expected_stocks and 
            scores_count >= expected_scores
        )
        
        return {
            "status": "ok",
            "database": "connected",
            "initialization_complete": initialization_complete,
            "progress": {
                "stocks": f"{stock_count}/{expected_stocks}",
                "scores": f"{scores_count}/{expected_scores}"
            }
        }
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
            
            # Use window function for efficient MA calculation
            prices_sql = text("""
                WITH prices AS (
                    SELECT 
                        date,
                        close,
                        ROW_NUMBER() OVER (ORDER BY date DESC) as rn
                    FROM stock_prices
                    WHERE stock_id = :stock_id
                    ORDER BY date DESC
                    LIMIT :days_needed
                ),
                ma_calc AS (
                    SELECT 
                        date,
                        close,
                        AVG(close) OVER (
                            ORDER BY date ASC
                            ROWS BETWEEN :ma_period-1 PRECEDING AND CURRENT ROW
                        ) as ma,
                        COUNT(*) OVER (
                            ORDER BY date ASC
                            ROWS BETWEEN :ma_period-1 PRECEDING AND CURRENT ROW
                        ) as window_size
                    FROM prices
                    ORDER BY date ASC
                )
                SELECT 
                    strftime('%Y-%m-%dT%H:%M:%SZ', date) as date,
                    ROUND(close, 4) as close,
                    CASE 
                        WHEN window_size >= :ma_period THEN ROUND(ma, 4)
                        ELSE NULL
                    END as ma
                FROM ma_calc
                ORDER BY date ASC
            """)
            
            prices = db.execute(
                prices_sql,
                {
                    "stock_id": stock.id,
                    "days_needed": days_needed,
                    "ma_period": int(period)
                }
            ).fetchall()
            
            result = [
                {
                    'date': price.date,
                    'price': float(price.close),
                    'ma': float(price.ma) if price.ma is not None else None
                }
                for price in prices
            ]
            
            return result
            
        price_data = list(reversed(get_cached_prices(cache_key)))
        
        # Date is already in ISO format from SQLite
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

@lru_cache(maxsize=1024)
def get_cached_stocks(params_str: str) -> Dict[str, Any]:
    """Get cached stock data using string parameters as cache key."""
    params = json.loads(params_str)
    with get_db_session() as db:
        try:
            return execute_stock_query(params, db)
        except Exception as e:
            print(f"Error executing stock query: {e}")
            # Clear cache on error to prevent stale data
            get_cached_stocks.cache_clear()
            raise

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
    
    # Get best suppression scores with proper normalization
    best_scores = (
        db.query(
            SuppressionScore.stock_id,
            SuppressionScore.ma_period,
            SuppressionScore.score,
            func.row_number().over(
                partition_by=SuppressionScore.stock_id,
                order_by=SuppressionScore.score.desc()
            ).label('rn')
        )
        .filter(SuppressionScore.ma_period.between(10, 60))  # Only consider MA10-MA60
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
        query = query.filter(Stock.index_type.in_([params["index_type"]]))
        
    # Create index hint for faster filtering
    query = query.with_hint(Stock, "USE INDEX (ix_stocks_index_type)")
    
    # Apply sorting with index hints
    if params["sort"] == "score":
        query = query.order_by(
            desc(best_scores.c.score) if params["order"] == "desc"
            else best_scores.c.score
        ).with_hint(SuppressionScore, "USE INDEX (ix_suppression_scores_score)")
    elif params["sort"] == "ma_period":
        query = query.order_by(
            desc(best_scores.c.ma_period) if params["order"] == "desc"
            else best_scores.c.ma_period
        ).with_hint(SuppressionScore, "USE INDEX (ix_suppression_scores_ma_period)")
    else:
        # Default sort by market cap with index hint
        query = query.order_by(desc(Stock.market_cap)).with_hint(Stock, "USE INDEX (ix_stocks_market_cap)")
    
    # Get total count directly from stocks table with filters and index hints
    count_query = db.query(Stock).with_hint(Stock, "USE INDEX (ix_stocks_index_type)")
    if params["search"]:
        count_query = count_query.filter(
            (Stock.symbol.ilike(f"%{params['search']}%")) |
            (Stock.name.ilike(f"%{params['search']}%"))
        )
    if params["index_type"]:
        count_query = count_query.filter(Stock.index_type.in_([params["index_type"]]))
    total_count = count_query.count()
    
    # Apply pagination
    page = max(params["page"], 1)
    limit = max(params["limit"], 1)
    offset = (page - 1) * limit
    query = query.offset(offset).limit(limit)
    
    # Execute query and format results
    stocks = []
    for stock, ma_period, score, latest_price, latest_date in query.all():
        # Handle NULL values with MA10 as baseline
        ma_period = ma_period or 10  # Default to MA10 if NULL (our normalization baseline)
        score = score or 0.0  # Default to 0.0 if NULL
        latest_price = latest_price or 0.0  # Default to 0.0 if NULL
        
        # Debug logging for score selection
        print(f"Selected MA{ma_period} for {stock.symbol} with score {score:.4f}")
        
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
