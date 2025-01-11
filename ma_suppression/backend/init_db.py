from app.main import engine, SessionLocal
from app.models import Base
from tests.test_pagination import create_test_data
from app.services.suppression_service import SuppressionService
import os

def init_database():
    db_file = "./ma_suppression.db"
    
    # Remove existing database file if it exists
    if os.path.exists(db_file):
        print(f"Removing existing database file: {db_file}")
        os.remove(db_file)
    
    print("Creating database tables...")
    Base.metadata.create_all(bind=engine)
    
    db = SessionLocal()
    try:
        print("Generating test data...")
        create_test_data(db)
        
        print("Calculating suppression scores...")
        suppression_service = SuppressionService(db)
        suppression_service.analyze_all_stocks()
        
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
