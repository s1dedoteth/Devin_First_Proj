from app.main import SessionLocal
from app.models import Stock, SuppressionScore

def check_database_status():
    """Check current database status."""
    db = SessionLocal()
    try:
        stock_count = db.query(Stock).count()
        score_count = db.query(SuppressionScore).count()
        print(f'Database status:\nStocks: {stock_count}\nScores: {score_count}')
        
        if stock_count > 0:
            # Sample some stocks
            stocks = db.query(Stock).limit(5).all()
            print("\nSample stocks:")
            for stock in stocks:
                print(f"{stock.symbol} ({stock.index_type})")
    finally:
        db.close()

if __name__ == "__main__":
    check_database_status()
