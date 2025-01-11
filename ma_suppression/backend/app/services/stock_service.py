import yfinance as yf
import pandas as pd
from sqlalchemy.orm import Session
from datetime import datetime, timedelta, timezone
from typing import List, Dict, Optional
import numpy as np
from ..models import Stock, StockPrice
import time
import requests
import io
import pytz

class StockService:
    def __init__(self, db: Session):
        self.db = db
        
    def fetch_full_nasdaq_symbols(self) -> List[str]:
        """Fetch complete list of NASDAQ stocks using multiple sources."""
        try:
            # Try Finviz first (most comprehensive)
            stocks = self._fetch_nasdaq_from_finviz()
            if len(stocks) > 1000:  # Reasonable minimum for NASDAQ
                return stocks
                
            # Try NASDAQ Trader
            stocks = self._fetch_nasdaq_from_trader()
            if len(stocks) > 1000:
                return stocks
                
            # Try QQQ holdings
            stocks = self._fetch_nasdaq_from_qqq()
            if len(stocks) > 100:  # QQQ usually has top holdings
                return stocks
                
            # Final fallback to static list
            return self._fetch_nasdaq_from_static()
            
        except Exception as e:
            print(f"Error in fetch_full_nasdaq_symbols: {e}")
            return self._fetch_nasdaq_from_static()
            
    def _fetch_nasdaq_from_finviz(self) -> List[str]:
        """Fetch NASDAQ stocks from Finviz."""
        try:
            stocks = []
            base_url = "https://finviz.com/screener.ashx"
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            }
            
            # Fetch first page to get total count
            params = {
                'v': '111',
                'f': 'exch_nasd',  # NASDAQ filter
                'r': '1',
                'o': '-marketcap'  # Sort by market cap descending
            }
            
            print(f"Fetching NASDAQ stocks from Finviz with params: {params}")
            response = requests.get(base_url, params=params, headers=headers)
            response.raise_for_status()
            
            # Use pandas to parse HTML tables with better error handling
            tables = pd.read_html(io.StringIO(response.text))
            if not tables:
                raise ValueError("No tables found in response")
                
            # Find the table with stock data (usually the last one)
            stock_table = None
            for table in reversed(tables):
                if len(table.columns) >= 2 and 'Ticker' in table.columns:
                    stock_table = table
                    break
                    
            if stock_table is None:
                raise ValueError("Could not find stock table")
                
            # Extract tickers
            tickers = stock_table['Ticker'].tolist()
            stocks.extend([str(t).strip() for t in tickers if pd.notna(t)])
            
            # Use fixed large number of pages to ensure we get all stocks
            total_pages = 150  # 150 pages * 20 stocks = 3000 stocks (more than enough)
            print(f"Using fixed {total_pages} pages to fetch NASDAQ stocks")
            
            # Fetch remaining pages
            for page in range(2, total_pages + 1):
                try:
                    params['r'] = str(1 + (page-1)*20)
                    print(f"Fetching NASDAQ page {page} with offset {params['r']}")
                    response = requests.get(base_url, params=params, headers=headers)
                    response.raise_for_status()
                    
                    tables = pd.read_html(io.StringIO(response.text))
                    stock_table = None
                    for table in reversed(tables):
                        if len(table.columns) >= 2 and any(col in table.columns for col in ['Ticker', 'Symbol', 'No.']):
                            stock_table = table
                            break
                            
                    if stock_table is not None:
                        ticker_col = next(col for col in stock_table.columns if col in ['Ticker', 'Symbol'])
                        tickers = stock_table[ticker_col].tolist()
                        stocks.extend([str(t).strip() for t in tickers if pd.notna(t)])
                        print(f"Found {len(stocks)} NASDAQ stocks so far...")
                    
                    # Rate limiting with progress update
                    time.sleep(0.5)
                    
                except Exception as e:
                    print(f"Error fetching page {page}: {e}")
                    continue
            
            # Clean and deduplicate
            stocks = list(set([s for s in stocks if s.isalpha()]))
            print(f"Found {len(stocks)} NASDAQ stocks from Finviz")
            return stocks
            
        except Exception as e:
            print(f"Error fetching from Finviz: {e}")
            return []
            
    def _fetch_nasdaq_from_trader(self) -> List[str]:
        """Fetch NASDAQ stocks from NASDAQ Trader."""
        try:
            url = "https://www.nasdaqtrader.com/dynamic/SymDir/nasdaqtraded.txt"
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            }
            
            response = requests.get(url, headers=headers)
            response.raise_for_status()
            
            content = '\n'.join(response.text.split('\n')[1:-1])  # Skip header and footer
            df = pd.read_csv(io.StringIO(content), delimiter='|')
            
            stocks = df[
                (df['Category'].isin(['Q', 'G', 'N'])) &  # Include all NASDAQ categories
                (df['Test Issue'] == 'N') &  # Not a test issue
                (df['Financial Status'].isin(['N', 'D', 'E', 'Q']))  # Include all valid statuses
            ]['Symbol'].tolist()
            
            stocks = [s.strip().split()[0] for s in stocks if isinstance(s, str)]
            stocks = [s for s in stocks if s.isalpha()]
            
            print(f"Found {len(stocks)} NASDAQ stocks from NASDAQ Trader")
            return stocks
            
        except Exception as e:
            print(f"Error fetching from NASDAQ Trader: {e}")
            return []
            
    def _fetch_nasdaq_from_qqq(self) -> List[str]:
        """Fetch NASDAQ stocks from QQQ holdings."""
        try:
            url = "https://www.invesco.com/us/financial-products/etfs/holdings/main/holdings/0?audienceType=Investor&action=download&ticker=QQQ"
            df = pd.read_csv(url)
            stocks = df['Holding Ticker'].dropna().tolist()
            stocks = [s.strip().split()[0] for s in stocks if isinstance(s, str)]
            stocks = [s for s in stocks if s.isalpha()]
            print(f"Found {len(stocks)} NASDAQ stocks from QQQ")
            return stocks
            
        except Exception as e:
            print(f"Error fetching from QQQ: {e}")
            return []
            
    def _fetch_nasdaq_from_static(self) -> List[str]:
        """Return a static list of major NASDAQ stocks."""
        stocks = [
            "AAPL", "MSFT", "AMZN", "NVDA", "META", "GOOGL", "GOOG", "TSLA",
            "AMD", "ADBE", "NFLX", "CSCO", "INTC", "CMCSA", "PEP", "AVGO",
            "COST", "TMUS", "QCOM", "TXN", "INTU", "AMAT", "ISRG", "ADP",
            "BKNG", "GILD", "MDLZ", "PYPL", "REGN", "VRTX", "ABNB", "ADI",
            "ASML", "CHTR", "LRCX", "MELI", "PANW", "SNPS", "WDAY", "CDNS"
        ]
        print(f"Using fallback list of {len(stocks)} NASDAQ stocks")
        return stocks

    def fetch_full_russell_symbols(self) -> List[str]:
        """Fetch complete list of Russell 2000 stocks using multiple sources."""
        try:
            # Try Finviz first (most comprehensive)
            stocks = self._fetch_russell_from_finviz()
            if len(stocks) > 1000:  # Reasonable minimum for Russell 2000
                return stocks
                
            # Try iShares
            stocks = self._fetch_russell_from_ishares()
            if len(stocks) > 1000:
                return stocks
                
            # Try Yahoo Finance
            stocks = self._fetch_russell_from_yfinance()
            if len(stocks) > 100:  # YFinance usually returns top holdings
                return stocks
                
            # Final fallback to static list
            return self._fetch_russell_from_static()
            
        except Exception as e:
            print(f"Error in fetch_full_russell_symbols: {e}")
            return self._fetch_russell_from_static()
            
    def _fetch_russell_from_finviz(self) -> List[str]:
        """Fetch Russell 2000 stocks from Finviz."""
        try:
            stocks = []
            base_url = "https://finviz.com/screener.ashx"
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            }
            
            # Fetch first page to get total count
            params = {
                'v': '111',
                'f': 'idx_russell2000',
                'r': '1',
                'o': '-marketcap'  # Sort by market cap descending
            }
            
            print(f"Fetching Russell 2000 stocks from Finviz with params: {params}")
            response = requests.get(base_url, params=params, headers=headers)
            response.raise_for_status()
            
            # Use pandas to parse HTML tables with better error handling
            tables = pd.read_html(io.StringIO(response.text))
            print(f"Found {len(tables)} tables in Russell 2000 response")
            if not tables:
                raise ValueError("No tables found in response")
                
            # Find the table with stock data (usually the last one)
            stock_table = None
            for table in reversed(tables):
                if len(table.columns) >= 2 and any(col in table.columns for col in ['Ticker', 'Symbol', 'No.']):
                    stock_table = table
                    break
                    
            if stock_table is None:
                raise ValueError("Could not find stock table")
                
            # Extract tickers
            tickers = stock_table['Ticker'].tolist()
            stocks.extend([str(t).strip() for t in tickers if pd.notna(t)])
            
            # Use fixed large number of pages to ensure we get all stocks
            total_pages = 150  # 150 pages * 20 stocks = 3000 stocks (more than enough)
            print(f"Using fixed {total_pages} pages to fetch Russell 2000 stocks")
            
            # Fetch remaining pages
            for page in range(2, total_pages + 1):
                try:
                    params['r'] = str(1 + (page-1)*20)
                    print(f"Fetching Russell 2000 page {page} with offset {params['r']}")
                    response = requests.get(base_url, params=params, headers=headers)
                    response.raise_for_status()
                    
                    tables = pd.read_html(io.StringIO(response.text))
                    stock_table = None
                    for table in reversed(tables):
                        if len(table.columns) >= 2 and any(col in table.columns for col in ['Ticker', 'Symbol', 'No.']):
                            stock_table = table
                            break
                            
                    if stock_table is not None:
                        ticker_col = next(col for col in stock_table.columns if col in ['Ticker', 'Symbol'])
                        tickers = stock_table[ticker_col].tolist()
                        stocks.extend([str(t).strip() for t in tickers if pd.notna(t)])
                        print(f"Found {len(stocks)} Russell 2000 stocks so far...")
                    
                    # Rate limiting with progress update
                    time.sleep(0.5)
                    
                except Exception as e:
                    print(f"Error fetching page {page}: {e}")
                    continue
            
            # Clean and deduplicate
            stocks = list(set([s for s in stocks if s.isalpha()]))
            print(f"Found {len(stocks)} Russell 2000 stocks from Finviz")
            return stocks
            
        except Exception as e:
            print(f"Error fetching from Finviz: {e}")
            return []
            
    def _fetch_russell_from_ishares(self) -> List[str]:
        """Fetch Russell 2000 stocks from iShares."""
        try:
            url = "https://www.ishares.com/us/products/239710/ishares-russell-2000-etf/1467271812596.ajax?fileType=csv&fileName=IWM_holdings&dataType=fund"
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            }
            
            response = requests.get(url, headers=headers)
            response.raise_for_status()
            
            # Try different CSV parsing options
            for sep in [',', '|', '\t']:
                try:
                    df = pd.read_csv(io.StringIO(response.text), sep=sep, on_bad_lines='skip')
                    ticker_column = next((col for col in df.columns if any(t in col.lower() for t in ['ticker', 'symbol'])), None)
                    if ticker_column:
                        break
                except Exception:
                    continue
            
            if not ticker_column:
                raise ValueError("Could not find ticker column")
                
            stocks = df[ticker_column].dropna().apply(lambda x: str(x).strip().split()[0]).tolist()
            stocks = [s for s in stocks if s.isalpha()]
            
            print(f"Found {len(stocks)} Russell 2000 stocks from iShares")
            return stocks
            
        except Exception as e:
            print(f"Error fetching from iShares: {e}")
            return []
            
    def _fetch_russell_from_yfinance(self) -> List[str]:
        """Fetch Russell 2000 stocks from Yahoo Finance."""
        try:
            iwm = yf.Ticker("IWM")
            info = iwm.info
            if 'holdings' in info:
                stocks = [h['symbol'] for h in info['holdings'] if 'symbol' in h]
                stocks = [s for s in stocks if s.isalpha()]
                print(f"Found {len(stocks)} Russell 2000 stocks from Yahoo Finance")
                return stocks
            raise ValueError("No holdings found in IWM info")
        except Exception as e:
            print(f"Error fetching from Yahoo Finance: {e}")
            return []
            
    def _fetch_russell_from_static(self) -> List[str]:
        """Return a static list of Russell 2000 stocks."""
        stocks = [
            "CROX", "AXON", "CELH", "IART", "EXAS", "PODD", "RH", "MEDP",
            "EXPO", "STAG", "SAIA", "STOR", "FIVE", "CVCO", "HALO", "RGEN",
            "OMCL", "NATI", "PNFP", "VRNT", "CTRE", "AMED", "CORT", "PRAA"
        ]
        print(f"Using fallback list of {len(stocks)} Russell 2000 stocks")
        return stocks
        
    def fetch_index_constituents(self) -> List[Dict[str, str]]:
        """Fetch all stocks from both Russell 2000 and NASDAQ."""
        nasdaq_symbols = self.fetch_full_nasdaq_symbols()
        russell_symbols = self.fetch_full_russell_symbols()
        
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
    
    def get_stock_info(self, symbol: str, index_type: str) -> Optional[Dict]:
        """Get stock information without market cap filtering."""
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
                    'last_updated': end_date.isoformat()
                }
            except requests.exceptions.RequestException as e:
                print(f"Network error fetching info for {symbol} (attempt {attempt + 1}): {e}")
                if attempt < max_retries - 1:
                    time.sleep(retry_delay * (attempt + 1))  # Exponential backoff
                continue
            except Exception as e:
                print(f"Error fetching info for {symbol} (attempt {attempt + 1}): {e}")
                if attempt < max_retries - 1:
                    time.sleep(retry_delay * (attempt + 1))
                continue
        
        print(f"Failed to fetch info for {symbol} after {max_retries} attempts")
        return None
    
    def fetch_daily_data(self, symbol: str, start_date: Optional[datetime] = None) -> pd.DataFrame:
        """Fetch daily OHLC data for a stock."""
        try:
            # Default to '6mo' period for sufficient historical data
            period = '6mo'
            if start_date:
                # If start_date is provided, calculate period dynamically
                days_diff = (datetime.now() - start_date).days
                if days_diff <= 5:
                    period = '5d'
                elif days_diff <= 30:
                    period = '1mo'
                elif days_diff <= 90:
                    period = '3mo'
                elif days_diff <= 180:
                    period = '6mo'
                else:
                    period = 'max'
                    
            # Download data using valid period
            stock = yf.Ticker(symbol)
            data = stock.history(period=period)
            if data.empty:
                print(f"No data available for {symbol} with period {period}")
                return pd.DataFrame()
                
            return data
            # Default to 2 years of data for MA200 calculations
            if start_date is None:
                start_date = datetime.now() - timedelta(days=730)
            # Clean symbol - remove spaces and special characters
            clean_symbol = symbol.strip().replace(' ', '')
            stock = yf.Ticker(clean_symbol)
            # Fetch with retry on empty data
            retries = 3
            for attempt in range(retries):
                df = stock.history(start=start_date)
                if not df.empty:
                    # Round to 4 decimal places for price precision
                    for col in ['Open', 'High', 'Low', 'Close']:
                        df[col] = df[col].round(4)
                    return df
                print(f"Attempt {attempt + 1}/{retries}: No data for {symbol}, retrying...")
                time.sleep(2)
            return pd.DataFrame()
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
    
    def update_all_data(self):
        """Update all stock data."""
        try:
            # Get list of stocks from indices
            stocks = self.fetch_index_constituents()
            
            # Get stock info for each symbol
            stock_info_list = []
            for stock in stocks:
                info = self.get_stock_info(stock['symbol'], stock['index_type'])
                if info:
                    stock_info_list.append(info)
            
            # Start date for historical data (2.5 years for reliable MA200 calculation)
            start_date = datetime.now() - timedelta(days=913)  # 2.5 years for padding
            
            success_count = 0
            error_count = 0
            
            # Add delay between batches to avoid rate limits
            batch_size = 25  # Reduced batch size
            batch_delay = 10  # Increased delay between batches
            
            # Process stocks in batches to avoid rate limits
            for i, stock_info in enumerate(stock_info_list):
                if i > 0 and i % batch_size == 0:
                    print(f"Sleeping for {batch_delay}s after processing {batch_size} stocks...")
                    time.sleep(batch_delay)
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
                "total_stocks": len(stock_info_list)
            }
        except Exception as e:
            print(f"Fatal error in update_all_data: {str(e)}")
            raise
