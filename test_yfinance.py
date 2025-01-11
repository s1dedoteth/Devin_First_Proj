import yfinance as yf
import pandas as pd
import pytz
from datetime import datetime, timedelta
from datetime import datetime, timedelta
import time

def test_yfinance():
    try:
        # Test with multiple stocks from different indices
        symbols = ['AAPL', 'MSFT', 'GOOGL', 'CROX', 'AXON', 'CELH']
        
        print('\nTesting batch download...')
        data = yf.download(symbols, period='1mo', group_by='ticker')
        print(f'\nSuccessfully downloaded data for {len(symbols)} stocks')
        
        for symbol in symbols:
            try:
                print(f'\nTesting {symbol}:')
                ticker = yf.Ticker(symbol)
                info = ticker.info
                print(f'Name: {info.get("longName")}')
                print(f'Market Cap: ${info.get("marketCap", 0) / 1e9:.2f}B')
                
                # Use explicit historical dates for testing (2023 data)
                start_str = '2023-01-01'
                end_str = '2023-12-31'
                print(f'Requesting historical data from {start_str} to {end_str}')
                hist = ticker.history(start=start_str, end=end_str)
                print(f'Got {len(hist)} days of data')
                
                # Handle timezone-aware comparison
                if not hist.empty:
                    try:
                        # Convert to NY timezone using pandas methods
                        ny_time = pd.Timestamp.now(tz='America/New_York')
                        
                        # Convert index to timezone-aware datetime
                        hist.index = pd.to_datetime(hist.index, utc=True).tz_convert('America/New_York')
                        
                        # Filter out future dates
                        hist = hist[hist.index <= ny_time]
                        if not hist.empty:
                            print(f'Historical Data Range: {hist.index.min()} to {hist.index.max()}')
                            print(f'Number of trading days: {len(hist)}')
                    except Exception as e:
                        print(f'Error processing {ticker.ticker}: {e}')
                else:
                    print('No historical data available')
                
                # Add delay to avoid rate limiting
                time.sleep(1)
                
            except Exception as e:
                print(f'Error processing {symbol}: {e}')
                continue
        
    except Exception as e:
        print(f'Error: {e}')

if __name__ == '__main__':
    test_yfinance()
