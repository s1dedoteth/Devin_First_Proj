from app.main import app, engine, SessionLocal
from app.models import Base, Stock, StockPrice, SuppressionScore
from sqlalchemy import inspect, func, desc, text
import time
import psutil
import os
import json

def get_memory_usage():
    """Get current memory usage in MB."""
    process = psutil.Process(os.getpid())
    return process.memory_info().rss / 1024 / 1024

def test_query_performance():
    """Test database query performance and index usage."""
    db = SessionLocal()
    try:
        print('\nTesting query performance...')
        print(f'Initial memory usage: {get_memory_usage():.1f} MB')
        
        # Test count query
        start = time.time()
        total = db.query(Stock).count()
        duration = time.time() - start
        print(f'\nCount query:')
        print(f'- Time: {duration:.2f}s')
        print(f'- Total stocks: {total}')
        print(f'- Memory: {get_memory_usage():.1f} MB')
        
        # Test basic pagination without joins
        start = time.time()
        stocks = db.query(Stock).order_by(Stock.symbol).offset(0).limit(50).all()
        duration = time.time() - start
        print(f'\nBasic pagination:')
        print(f'- Time: {duration:.2f}s')
        print(f'- Results: {len(stocks)}')
        print(f'- Memory: {get_memory_usage():.1f} MB')
        
        # Test paginated query with joins and subqueries (actual production query)
        start = time.time()
        subq = (
            db.query(
                SuppressionScore.stock_id,
                func.max(SuppressionScore.score).label('max_score')
            )
            .group_by(SuppressionScore.stock_id)
            .subquery()
        )
        
        query = db.query(
            Stock,
            SuppressionScore.ma_period,
            SuppressionScore.score,
            StockPrice.close,
            StockPrice.date
        ).join(
            subq, Stock.id == subq.c.stock_id
        ).join(
            SuppressionScore,
            (SuppressionScore.stock_id == Stock.id) & 
            (SuppressionScore.score == subq.c.max_score)
        ).join(
            StockPrice,
            Stock.id == StockPrice.stock_id
        ).order_by(
            desc(SuppressionScore.score)
        ).limit(50)
        
        result = query.all()
        duration = time.time() - start
        print(f'\nComplex pagination:')
        print(f'- Time: {duration:.2f}s')
        print(f'- Results: {len(result)}')
        print(f'- Memory: {get_memory_usage():.1f} MB')
        
        # Test index existence
        inspector = inspect(engine)
        
        def print_indexes(table_name):
            indexes = inspector.get_indexes(table_name)
            print(f'\nIndexes on {table_name}:')
            for idx in indexes:
                print(f"- {idx['name']}: {idx['column_names']} (unique: {idx.get('unique', False)})")
        
        print_indexes('stocks')
        print_indexes('stock_prices')
        print_indexes('suppression_scores')
        
        # Test index effectiveness
        print('\nAnalyzing index usage...')
        for table in ['stocks', 'stock_prices', 'suppression_scores']:
            start = time.time()
            count = db.execute(text(f'SELECT COUNT(*) FROM {table}')).scalar()
            print(f'\n{table}:')
            print(f'- Row count: {count}')
            print(f'- Count query time: {time.time() - start:.4f}s')
            
            if table == 'suppression_scores':
                # Test score index
                start = time.time()
                db.query(SuppressionScore).order_by(
                    SuppressionScore.score.desc()
                ).limit(10).all()
                print(f'- Score index query time: {time.time() - start:.4f}s')
            
            elif table == 'stock_prices':
                # Test date index
                start = time.time()
                db.query(StockPrice).order_by(
                    StockPrice.date.desc()
                ).limit(10).all()
                print(f'- Date index query time: {time.time() - start:.4f}s')
        
    finally:
        db.close()

if __name__ == '__main__':
    test_query_performance()
