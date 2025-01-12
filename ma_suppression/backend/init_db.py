from app.main import engine, SessionLocal
from app.models import Base
from tests.test_pagination import create_test_data
from app.services.suppression_service import SuppressionService
import os

def init_database():
    # Use same database path as main.py
    db_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data")
    os.makedirs(db_dir, exist_ok=True)
    db_file = os.path.join(db_dir, "ma_suppression.db")
    print(f"Using database file: {db_file}")
    
    # Remove existing database file if it exists
    if os.path.exists(db_file):
        print(f"Removing existing database file: {db_file}")
        os.remove(db_file)
        
    # Ensure directory has proper permissions
    os.chmod(db_dir, 0o777)
    
    print("Creating database tables...")
    # Drop all tables first
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    
    db = SessionLocal()
    try:
        print("Generating test data...")
        create_test_data(db)
        
        print("Calculating suppression scores...")
        suppression_service = SuppressionService(db)
        import asyncio
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        loop.run_until_complete(suppression_service.analyze_all_stocks())
        loop.close()
        
        # Verify database contents
        from app.models import Stock, SuppressionScore
        stock_count = db.query(Stock).count()
        score_count = db.query(SuppressionScore).count()
        print(f"\nDatabase initialization complete:")
        print(f"- Stocks: {stock_count}")
        print(f"- Scores: {score_count}")
        
    except Exception as e:
        print(f"Error during database initialization: {e}")
        raise
    finally:
        db.close()

if __name__ == "__main__":
    init_database()
