import yfinance as yf
import pandas as pd
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from typing import List, Dict
from ..models import Stock, StockPrice

class StockService:
    def __init__(self, db: Session):
        self.db = db
        
    def fetch_index_constituents(self) -> List[str]:
        """Fetch Russell 2000 and NASDAQ stocks."""
        # For Russell 2000, we use the IWM ETF holdings
        russell = yf.Ticker("IWM")
        russell_holdings = russell.holdings
        russell_symbols = russell_holdings.index.tolist() if russell_holdings is not None else []
        
        # For NASDAQ, we use the QQQ ETF holdings
        nasdaq = yf.Ticker("QQQ")
        nasdaq_holdings = nasdaq.holdings
        nasdaq_symbols = nasdaq_holdings.index.tolist() if nasdaq_holdings is not None else []
        
        return list(set(russell_symbols + nasdaq_symbols))
    
    def filter_by_market_cap(self, symbols: List[str], min_cap: float = 10e9) -> List[Dict]:
        """Filter stocks by market cap (>$10B)."""
        filtered_stocks = []
        for symbol in symbols:
            try:
                stock = yf.Ticker(symbol)
                info = stock.info
                if info.get('marketCap', 0) > min_cap:
                    filtered_stocks.append({
                        'symbol': symbol,
                        'name': info.get('longName', ''),
                        'market_cap': info.get('marketCap', 0),
                        'index_type': 'RUSSELL2000' if symbol in symbols else 'NASDAQ'
                    })
            except Exception as e:
                print(f"Error fetching info for {symbol}: {e}")
                continue
        return filtered_stocks
    
    def fetch_daily_data(self, symbol: str, start_date: datetime) -> pd.DataFrame:
        """Fetch daily OHLC data for a stock."""
        try:
            stock = yf.Ticker(symbol)
            df = stock.history(start=start_date)
            # Round to 4 decimal places for price precision
            for col in ['Open', 'High', 'Low', 'Close']:
                df[col] = df[col].round(4)
            return df
        except Exception as e:
            print(f"Error fetching data for {symbol}: {e}")
            return pd.DataFrame()
    
    def store_stock_data(self, stock_info: Dict) -> Stock:
        """Store stock information in database."""
        stock = Stock(
            symbol=stock_info['symbol'],
            name=stock_info['name'],
            market_cap=stock_info['market_cap'],
            index_type=stock_info['index_type']
        )
        self.db.add(stock)
        self.db.commit()
        self.db.refresh(stock)
        return stock
    
    def store_price_data(self, stock: Stock, price_data: pd.DataFrame):
        """Store daily price data in database."""
        for date, row in price_data.iterrows():
            price = StockPrice(
                stock_id=stock.id,
                date=date,
                open=row['Open'],
                high=row['High'],
                low=row['Low'],
                close=row['Close']
            )
            self.db.add(price)
        self.db.commit()
    
    def update_all_data(self):
        """Update all stock data."""
        # Get list of stocks from indices
        symbols = self.fetch_index_constituents()
        
        # Filter by market cap
        filtered_stocks = self.filter_by_market_cap(symbols)
        
        # Start date for historical data (e.g., 1 year ago)
        start_date = datetime.now() - timedelta(days=365)
        
        # Process each stock
        for stock_info in filtered_stocks:
            # Store or update stock info
            stock = self.store_stock_data(stock_info)
            
            # Fetch and store price data
            price_data = self.fetch_daily_data(stock_info['symbol'], start_date)
            if not price_data.empty:
                self.store_price_data(stock, price_data)
