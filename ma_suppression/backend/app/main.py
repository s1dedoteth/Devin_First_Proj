from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker, Session
from .models import Base, Stock, StockPrice, SuppressionScore
from .services.stock_service import StockService
from .services.scheduler import setup_scheduler

# PostgreSQL database configuration
SQLALCHEMY_DATABASE_URL = "postgresql://devin:devin123@localhost:5432/ma_suppression"
engine = create_engine(SQLALCHEMY_DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create all tables
Base.metadata.create_all(bind=engine)

app = FastAPI()

# Initialize scheduler on startup
@app.on_event("startup")
async def startup_event():
    """Initialize scheduler on startup."""
    db = SessionLocal()
    try:
        setup_scheduler(db)
    finally:
        db.close()

# Disable CORS. Do not remove this for full-stack development.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
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
        return {"status": "success", "message": "Stock data update initiated"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to update stock data: {str(e)}")

@app.get("/api/stocks")
async def get_stocks(db: Session = Depends(get_db)):
    """Get list of stocks with their latest prices."""
    try:
        stocks = db.query(Stock).all()
        result = []
        for stock in stocks:
            latest_price = (
                db.query(StockPrice)
                .filter(StockPrice.stock_id == stock.id)
                .order_by(StockPrice.date.desc())
                .first()
            )
            result.append({
                "symbol": stock.symbol,
                "name": stock.name,
                "market_cap": stock.market_cap,
                "index_type": stock.index_type,
                "latest_price": latest_price.close if latest_price else None,
                "latest_date": latest_price.date if latest_price else None
            })
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch stocks: {str(e)}")
