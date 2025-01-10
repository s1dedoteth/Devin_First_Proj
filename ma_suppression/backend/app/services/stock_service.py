import yfinance as yf
import pandas as pd
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from typing import List, Dict
from ..models import Stock, StockPrice

class StockService:
    # Sample NASDAQ symbols (top companies)
    NASDAQ_SYMBOLS = {
        "AAPL", "MSFT", "AMZN", "NVDA", "GOOGL", "META", "TSLA", "AVGO", "PEP", "COST",
        "ADBE", "CSCO", "TMUS", "CMCSA", "INTC", "AMD", "INTU", "QCOM", "AMAT", "ISRG"
    }
    
    def __init__(self, db: Session):
        self.db = db
        
    def fetch_index_constituents(self) -> List[str]:
        """Fetch Russell 2000 and NASDAQ stocks."""
        # For demonstration, we'll use a sample of major stocks
        # In production, this should be replaced with a proper data source
        # You might want to use a paid API service for complete listings
        sample_stocks = [
            # NASDAQ-100 top companies
            "AAPL", "MSFT", "AMZN", "NVDA", "GOOGL", "META", "TSLA", "AVGO", "PEP", "COST",
            "ADBE", "CSCO", "TMUS", "CMCSA", "INTC", "AMD", "INTU", "QCOM", "AMAT", "ISRG",
            
            # Russell 2000 representatives (small-cap stocks)
            "CROX", "DECK", "AXON", "GTLS", "PODD", "MEDP", "ENPH", "TREX", "FIVE", "FOXF",
            "EXAS", "PLTK", "LSCC", "ACAD", "PNFP", "CVLT", "HALO", "ICUI", "OMCL", "VRNS"
        ]
        
        print(f"Fetching data for {len(sample_stocks)} sample stocks...")
        return sample_stocks
    
    def filter_by_market_cap(self, symbols: List[str], min_cap: float = 10e9) -> List[Dict]:
        """Filter stocks by market cap (>$10B)."""
        filtered_stocks = []
        for symbol in symbols:
            try:
                stock = yf.Ticker(symbol)
                # Use a batch request to get info
                info = stock.fast_info
                market_cap = info.market_cap if hasattr(info, 'market_cap') else 0
                
                if market_cap > min_cap:
                    filtered_stocks.append({
                        'symbol': symbol,
                        'name': stock.info.get('longName', symbol),
                        'market_cap': market_cap,
                        'index_type': 'NASDAQ' if symbol in self.NASDAQ_SYMBOLS else 'RUSSELL2000'
                    })
                    print(f"Added {symbol} with market cap ${market_cap/1e9:.2f}B")
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
        """Store or update stock information in database."""
        # Check if stock exists
        stock = self.db.query(Stock).filter(Stock.symbol == stock_info['symbol']).first()
        
        if stock:
            # Update existing stock
            stock.name = stock_info['name']
            stock.market_cap = stock_info['market_cap']
            stock.index_type = stock_info['index_type']
        else:
            # Create new stock
            stock = Stock(
                symbol=stock_info['symbol'],
                name=stock_info['name'],
                market_cap=stock_info['market_cap'],
                index_type=stock_info['index_type']
            )
            self.db.add(stock)
        
        try:
            self.db.commit()
            self.db.refresh(stock)
        except Exception as e:
            print(f"Error storing stock data: {e}")
            self.db.rollback()
            raise
        
        return stock
    
    def store_price_data(self, stock: Stock, price_data: pd.DataFrame):
        """Store daily price data in database."""
        # Reset index to make date a column
        price_data = price_data.reset_index()
        
        for _, row in price_data.iterrows():
            try:
                # Convert numpy types to native Python types
                price = StockPrice(
                    stock_id=stock.id,
                    date=row['Date'].date(),  # Pandas Timestamp to date
                    open=float(row['Open'].item()),  # numpy.float64 to float
                    high=float(row['High'].item()),
                    low=float(row['Low'].item()),
                    close=float(row['Close'].item())
                )
                self.db.add(price)
            except Exception as e:
                print(f"Error storing price data: {e}")
                continue
        
        try:
            self.db.commit()
        except Exception as e:
            print(f"Error committing price data: {e}")
            self.db.rollback()
    
    def update_all_data(self):
        """Update all stock data."""
        try:
            # Get list of stocks from indices
            symbols = self.fetch_index_constituents()
            
            # Filter by market cap
            filtered_stocks = self.filter_by_market_cap(symbols)
            
            # Start date for historical data (e.g., 1 year ago)
            start_date = datetime.now() - timedelta(days=365)
            
            success_count = 0
            error_count = 0
            
            # Process each stock
            for stock_info in filtered_stocks:
                try:
                    # Store or update stock info
                    stock = self.store_stock_data(stock_info)
                    
                    # Fetch and store price data
                    price_data = self.fetch_daily_data(stock_info['symbol'], start_date)
                    if not price_data.empty:
                        # Clear existing price data for this stock
                        self.db.query(StockPrice).filter(
                            StockPrice.stock_id == stock.id
                        ).delete()
                        
                        # Store new price data
                        self.store_price_data(stock, price_data)
                        success_count += 1
                        print(f"Successfully updated {stock_info['symbol']} with {len(price_data)} price records")
                    else:
                        print(f"No price data available for {stock_info['symbol']}")
                        error_count += 1
                except Exception as e:
                    print(f"Error processing {stock_info['symbol']}: {str(e)}")
                    error_count += 1
                    continue
            
            return {
                "status": "completed",
                "success_count": success_count,
                "error_count": error_count,
                "total_stocks": len(filtered_stocks)
            }
        except Exception as e:
            print(f"Fatal error in update_all_data: {str(e)}")
            raise
