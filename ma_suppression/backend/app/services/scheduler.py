from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from sqlalchemy.orm import Session
from .stock_service import StockService

def setup_scheduler(db: Session):
    """Set up daily updates for stock data."""
    scheduler = BackgroundScheduler()
    stock_service = StockService(db)
    
    # Schedule daily update at market close (4 PM EST)
    scheduler.add_job(
        stock_service.update_all_data,
        trigger=CronTrigger(hour=16, timezone='America/New_York'),
        id='update_stock_data',
        name='Daily stock data update',
        replace_existing=True
    )
    
    scheduler.start()
    return scheduler
