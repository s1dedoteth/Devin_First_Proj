import yfinance as yf
import pandas as pd
from sqlalchemy.orm import Session
from datetime import datetime, timedelta, timezone
from typing import List, Dict, Optional, Union, Any
import numpy as np
from ..models import Stock, StockPrice
import time
import asyncio
import io
import pytz
import requests
from .cache_service import cache_service

# Try to import aiohttp, fallback to requests if not available
try:
    import aiohttp
    AIOHTTP_AVAILABLE = True
except ImportError:
    AIOHTTP_AVAILABLE = False
    print("aiohttp not available, using requests as fallback")

async def async_get(url: str, timeout: int = 10) -> Dict[str, Any]:
    """Make HTTP GET request with fallback from aiohttp to requests."""
    if AIOHTTP_AVAILABLE:
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url, timeout=timeout) as response:
                    return await response.json()
        except Exception as e:
            print(f"aiohttp request failed: {e}, falling back to requests")
            
    # Synchronous fallback using requests
    try:
        response = requests.get(url, timeout=timeout)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        print(f"Request failed: {e}")
        return {}

# Type alias for async/sync function results
StockList = Union[List[str], asyncio.Future[List[str]]]

class StockService:
    def __init__(self, db: Session):
        self.db = db
        
    @cache_service.cache_method("nasdaq_symbols", ttl_memory=3600, ttl_disk=86400)
    async def fetch_full_nasdaq_symbols(self) -> List[str]:
        """Fetch complete list of NASDAQ stocks using yfinance with caching."""
        try:
            # Use QQQ (NASDAQ-100 ETF) to get NASDAQ stocks
            loop = asyncio.get_event_loop()
            qqq = await loop.run_in_executor(None, yf.Ticker, "QQQ")
            info = await loop.run_in_executor(None, lambda: qqq.info)
            
            if 'holdings' in info:
                stocks = [h['symbol'] for h in info['holdings'] if 'symbol' in h]
                stocks = [s for s in stocks if s.isalpha()]
                print(f"Found {len(stocks)} NASDAQ stocks from QQQ")
                return stocks
                
            # Fallback to static list if QQQ fails
            return self._fetch_nasdaq_from_static()
            
        except Exception as e:
            print(f"Error in fetch_full_nasdaq_symbols: {e}")
            return self._fetch_nasdaq_from_static()
            

            
    def _fetch_nasdaq_from_static(self) -> List[str]:
        """Return a static list of major NASDAQ stocks with caching."""
        cache_key = "nasdaq_static_list"
        cached_stocks = cache_service.get_from_memory(cache_key)
        if cached_stocks:
            print("Using cached static NASDAQ list")
            return cached_stocks
            
        # Expanded list of NASDAQ stocks for better coverage
        stocks = [
            "AAPL", "MSFT", "AMZN", "NVDA", "META", "GOOGL", "GOOG", "TSLA",
            "AMD", "ADBE", "NFLX", "CSCO", "INTC", "CMCSA", "PEP", "AVGO",
            "COST", "TMUS", "QCOM", "TXN", "INTU", "AMAT", "ISRG", "ADP",
            "BKNG", "GILD", "MDLZ", "PYPL", "REGN", "VRTX", "ABNB", "ADI",
            "ASML", "CHTR", "LRCX", "MELI", "PANW", "SNPS", "WDAY", "CDNS",
            "KLAC", "MCHP", "NXPI", "PAYX", "ROST", "SGEN", "SIRI", "SWKS",
            "VRSK", "VRSN", "XLNX", "ZM", "DOCU", "DXCM", "FAST", "FISV",
            "IDXX", "ILMN", "KDP", "LULU", "MAR", "MNST", "MTCH", "ODFL"
        ]
        print(f"Using fallback list of {len(stocks)} NASDAQ stocks")
        
        # Cache the static list (longer TTL since it rarely changes)
        cache_service.set_in_memory(cache_key, stocks, ttl=86400)  # Cache for 24 hours
        return stocks

    @cache_service.cache_method("russell_symbols", ttl_memory=3600, ttl_disk=86400)
    async def fetch_full_russell_symbols(self) -> List[str]:
        """Fetch complete list of Russell 2000 stocks using yfinance with caching."""
        try:
            # Use IWM (Russell 2000 ETF) to get Russell 2000 stocks
            loop = asyncio.get_event_loop()
            iwm = await loop.run_in_executor(None, yf.Ticker, "IWM")
            info = await loop.run_in_executor(None, lambda: iwm.info)
            
            if 'holdings' in info:
                stocks = [h['symbol'] for h in info['holdings'] if 'symbol' in h]
                stocks = [s for s in stocks if s.isalpha()]
                print(f"Found {len(stocks)} Russell 2000 stocks from IWM")
                return stocks
                
            # Fallback to static list if IWM fails
            return self._fetch_russell_from_static()
            
        except Exception as e:
            print(f"Error in fetch_full_russell_symbols: {e}")
            return self._fetch_russell_from_static()
            

            
    def _fetch_russell_from_static(self) -> List[str]:
        """Return a static list of Russell 2000 stocks with caching."""
        cache_key = "russell_static_list"
        cached_stocks = cache_service.get_from_memory(cache_key)
        if cached_stocks:
            print("Using cached static Russell 2000 list")
            return cached_stocks
            
        # Expanded list of Russell 2000 stocks for better coverage
        stocks = [
            "CROX", "AXON", "CELH", "IART", "EXAS", "PODD", "RH", "MEDP",
            "EXPO", "STAG", "SAIA", "STOR", "FIVE", "CVCO", "HALO", "RGEN",
            "OMCL", "NATI", "PNFP", "VRNT", "CTRE", "AMED", "CORT", "PRAA",
            "ACAD", "ADTN", "AEIS", "AGYS", "ALRM", "AMSF", "APEI", "ARCB",
            "AVAV", "AVID", "AVNS", "AXTI", "BBSI", "BCOR", "BCOV", "BEAT",
            "BGCP", "BGSF", "BKTI", "BLDR", "BMCH", "BOOM", "BOOT", "BRKS",
            "CCMP", "CCOI", "CCRN", "CEVA", "CHEF", "CHUY", "CLAR", "CLFD"
        ]
        print(f"Using fallback list of {len(stocks)} Russell 2000 stocks")
        
        # Cache the static list (longer TTL since it rarely changes)
        cache_service.set_in_memory(cache_key, stocks, ttl=86400)  # Cache for 24 hours
        return stocks
        
    @cache_service.cache_method("index_constituents", ttl_memory=3600, ttl_disk=86400)
    async def fetch_index_constituents(self) -> List[Dict[str, str]]:
        """Fetch all stocks from both Russell 2000 and NASDAQ with caching."""
        nasdaq_symbols = await self.fetch_full_nasdaq_symbols()
        russell_symbols = await self.fetch_full_russell_symbols()
        
        # Create list of dictionaries with symbol and index type
        stocks = []
        
        # Add NASDAQ stocks
        for symbol in nasdaq_symbols:
            stocks.append({
                'symbol': symbol,
                'index_type': 'NASDAQ'
            })
            
        # Add Russell 2000 stocks (include all)
        for symbol in russell_symbols:
            stocks.append({
                'symbol': symbol,
                'index_type': 'RUSSELL2000'
            })
        
        print(f"Fetched {len(stocks)} total stocks "
              f"({len(nasdaq_symbols)} NASDAQ, {len(russell_symbols)} Russell 2000)")
        return stocks
    
    @cache_service.cache_method("stock_info", ttl_memory=300, ttl_disk=3600)
    async def get_stock_info(self, symbol: str, index_type: str) -> Optional[Dict]:
        """Get stock information with caching."""
        max_retries = 3
        retry_delay = 1
        
        # Clean symbol - remove spaces and special characters
        clean_symbol = symbol.strip().replace(' ', '')
        
        # Use explicit historical date range (previous year)
        today = datetime.now()
        end_year = today.year - 1  # Use previous year's data
        end_str = f'{end_year}-12-31'
        start_str = f'{end_year}-01-01'
        print(f"Fetching historical data for {symbol} from {start_str} to {end_str}")
        
        for attempt in range(max_retries):
            try:
                stock = yf.Ticker(clean_symbol)
                # Get both fast_info and regular info
                fast_info = stock.fast_info
                info = stock.info
                
                # Download historical data with string dates
                print(f"Fetching {symbol} data from {start_str} to {end_str}")
                data = stock.history(start=start_str, end=end_str)
                if data.empty:
                    print(f"No data returned for {symbol}")
                    return None
                
                # Handle timezone-aware comparison
                try:
                    # Convert to NY timezone for consistency
                    data.index = pd.to_datetime(data.index).tz_localize('UTC').tz_convert('America/New_York')
                    
                    # Verify data range
                    if not data.empty:
                        print(f"Got data for {symbol}: {data.index.min()} to {data.index.max()}")
                    else:
                        print(f"Empty data after timezone conversion for {symbol}")
                        return None
                except Exception as e:
                    print(f"Error handling dates for {symbol}: {e}")
                    return None
                
                # Try different ways to get market cap
                market_cap = (
                    getattr(fast_info, 'market_cap', None) or
                    info.get('marketCap', 0)
                )
                
                # Get company name
                name = (
                    info.get('longName') or
                    info.get('shortName') or
                    symbol
                )
                
                # Handle rate limiting
                time.sleep(0.5)  # Increased delay to avoid rate limits
                
                return {
                    'symbol': symbol,
                    'name': name,
                    'market_cap': market_cap,
                    'index_type': index_type,
                    'last_updated': datetime.now(pytz.UTC).isoformat()
                }
            except Exception as e:
                error_type = "Network error" if AIOHTTP_AVAILABLE and isinstance(e, aiohttp.ClientError) else "Error"
                print(f"{error_type} fetching info for {symbol} (attempt {attempt + 1}): {e}")
                if attempt < max_retries - 1:
                    await asyncio.sleep(retry_delay * (attempt + 1))  # Exponential backoff
                continue
        
        print(f"Failed to fetch info for {symbol} after {max_retries} attempts")
        return None
    
    async def fetch_daily_data(self, symbol: str, start_date: Optional[datetime] = None) -> pd.DataFrame:
        """Fetch daily OHLC data for a stock with caching."""
        try:
            # Clean symbol and generate cache key
            clean_symbol = symbol.strip().replace(' ', '')
            days = (datetime.now() - start_date).days if start_date else 180  # Default to 6 months
            cache_key = f"daily_data_{clean_symbol}_{days}"
            
            # Check cache first
            cached_data = cache_service.get_from_memory(cache_key)
            if cached_data is not None:
                print(f"Using cached daily data for {symbol}")
                return pd.DataFrame(cached_data)

            # Run yfinance operations in thread pool
            loop = asyncio.get_event_loop()
            stock = await loop.run_in_executor(None, yf.Ticker, clean_symbol)
            
            # Calculate period based on days
            period = '6mo'  # Default
            if days <= 5:
                period = '5d'
            elif days <= 30:
                period = '1mo'
            elif days <= 90:
                period = '3mo'
            elif days > 180:
                period = 'max'
            
            # Fetch data with retries
            max_retries = 3
            for attempt in range(max_retries):
                try:
                    # Use explicit date range if provided
                    if start_date:
                        hist = await loop.run_in_executor(
                            None,
                            lambda: stock.history(start=start_date.strftime('%Y-%m-%d'))
                        )
                    else:
                        hist = await loop.run_in_executor(
                            None,
                            lambda: stock.history(period=period)
                        )
                    
                    if not hist.empty:
                        # Handle timezone
                        hist.index = pd.to_datetime(hist.index).tz_localize('UTC').tz_convert('America/New_York')
                        
                        # Round to 4 decimal places for price precision
                        for col in ['Open', 'High', 'Low', 'Close']:
                            hist[col] = hist[col].round(4)
                        
                        # Cache the results
                        cache_data = hist.reset_index().to_dict('records')
                        cache_service.set_in_memory(cache_key, cache_data, ttl=1800)  # 30 minutes
                        
                        return hist
                    
                    print(f"Attempt {attempt + 1}/{max_retries}: No data for {symbol}, retrying...")
                    await asyncio.sleep(2)
                    
                except Exception as e:
                    print(f"Error on attempt {attempt + 1} for {symbol}: {e}")
                    if attempt < max_retries - 1:
                        await asyncio.sleep(2)
                    continue
            
            print(f"Failed to fetch data for {symbol} after {max_retries} attempts")
            return pd.DataFrame()
            
        except Exception as e:
            print(f"Error fetching data for {symbol}: {e}")
            return pd.DataFrame()
    
    def store_stock_data(self, stock_info: Dict) -> Stock:
        """Store or update stock information in database.
        Maintains separate entries for stocks that exist in both indices."""
        # Check if stock exists with the same symbol AND index_type
        stock = self.db.query(Stock).filter(
            Stock.symbol == stock_info['symbol'],
            Stock.index_type == stock_info['index_type']
        ).first()
        
        if stock:
            # Update existing stock, preserving its index_type
            stock.name = stock_info['name']
            stock.market_cap = stock_info['market_cap']
            # Don't update index_type as it's part of the unique identifier
        else:
            # Create new stock entry
            stock = Stock(
                symbol=stock_info['symbol'],
                name=stock_info['name'],
                market_cap=stock_info['market_cap'],
                index_type=stock_info['index_type']
            )
            self.db.add(stock)
            print(f"Adding new stock: {stock_info['symbol']} ({stock_info['index_type']})")
        
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
        try:
            # Clear existing price data for this stock
            self.db.query(StockPrice).filter(StockPrice.stock_id == stock.id).delete()
            self.db.commit()
            
            # Convert DataFrame to records for bulk insertion
            records = []
            
            # Convert DataFrame to dictionary of records
            price_dict = price_data.round(4).reset_index().to_dict('records')
            
            for record in price_dict:
                records.append(
                    StockPrice(
                        stock_id=stock.id,
                        date=record['Date'].date(),
                        open=float(record['Open']),
                        high=float(record['High']),
                        low=float(record['Low']),
                        close=float(record['Close'])
                    )
                )
            
            # Bulk insert all records
            self.db.bulk_save_objects(records)
            self.db.commit()
            print(f"Successfully stored {len(records)} price records for {stock.symbol}")
            
        except Exception as e:
            print(f"Error storing price data for {stock.symbol}: {e}")
            self.db.rollback()
    
    async def update_all_data(self):
        """Update all stock data."""
        try:
            # Get list of stocks from indices
            stocks = await self.fetch_index_constituents()
            
            # Get stock info for each symbol in parallel batches
            batch_size = 10  # Process 10 stocks at a time
            stock_info_list = []
            
            for i in range(0, len(stocks), batch_size):
                batch = stocks[i:i + batch_size]
                tasks = []
                
                for stock in batch:
                    task = asyncio.create_task(
                        self.get_stock_info(stock['symbol'], stock['index_type'])
                    )
                    tasks.append(task)
                
                # Wait for batch to complete
                results = await asyncio.gather(*tasks, return_exceptions=True)
                
                # Filter out errors and None results
                for result in results:
                    if result and not isinstance(result, Exception):
                        stock_info_list.append(result)
                
                # Add delay between batches to avoid rate limits
                await asyncio.sleep(2)
            
            # Start date for historical data (2.5 years for reliable MA200 calculation)
            start_date = datetime.now() - timedelta(days=913)  # 2.5 years for padding
            
            success_count = 0
            error_count = 0
            
            # Process stocks in parallel batches
            batch_size = 5  # Smaller batch size for price data
            for i in range(0, len(stock_info_list), batch_size):
                batch = stock_info_list[i:i + batch_size]
                tasks = []
                
                for stock_info in batch:
                    task = asyncio.create_task(self._update_single_stock(stock_info, start_date))
                    tasks.append(task)
                
                # Wait for batch to complete
                results = await asyncio.gather(*tasks, return_exceptions=True)
                
                # Process results
                for result in results:
                    if isinstance(result, Exception):
                        error_count += 1
                        print(f"Error in batch: {result}")
                    elif result:  # True indicates success
                        success_count += 1
                
                # Add delay between batches
                await asyncio.sleep(5)
                print(f"Progress: {success_count + error_count}/{len(stock_info_list)} stocks processed")
            
            return {
                "status": "completed",
                "success_count": success_count,
                "error_count": error_count,
                "total_stocks": len(stock_info_list)
            }
            
        except Exception as e:
            print(f"Fatal error in update_all_data: {str(e)}")
            raise
            
    async def _update_single_stock(self, stock_info: Dict, start_date: datetime) -> bool:
        """Update data for a single stock."""
        try:
            # Store or update stock info
            loop = asyncio.get_event_loop()
            stock = await loop.run_in_executor(
                None,
                lambda: self.store_stock_data(stock_info)
            )
            
            # Fetch and store price data
            price_data = await self.fetch_daily_data(stock_info['symbol'], start_date)
            if not price_data.empty:
                # Run database operations in thread pool
                await loop.run_in_executor(
                    None,
                    lambda: (
                        self.db.query(StockPrice)
                        .filter(StockPrice.stock_id == stock.id)
                        .delete()
                    )
                )
                
                await loop.run_in_executor(
                    None,
                    lambda: self.store_price_data(stock, price_data)
                )
                
                print(f"Successfully updated {stock_info['symbol']} with {len(price_data)} price records")
                return True
            else:
                print(f"No price data available for {stock_info['symbol']}")
                return False
                
        except Exception as e:
            print(f"Error processing {stock_info['symbol']}: {str(e)}")
            return False
