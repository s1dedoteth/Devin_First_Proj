from app.main import app, engine
from app.models import Base, Stock

def test_database():
    try:
        # Create all tables
        Base.metadata.create_all(bind=engine)
        print('Database connection successful and tables created')
    except Exception as e:
        print(f'Database connection failed: {e}')

if __name__ == '__main__':
    test_database()
