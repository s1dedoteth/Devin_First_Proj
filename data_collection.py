import yfinance as yf
import pandas as pd
from datetime import datetime, timedelta
import os

def download_stock_data(symbol, start_date, end_date):
    """Download historical stock data from Yahoo Finance."""
    try:
        stock = yf.Ticker(symbol)
        df = stock.history(start=start_date, end=end_date)
        return df
    except Exception as e:
        print(f"Error downloading {symbol}: {str(e)}")
        return None

def main():
    # Create data directory if it doesn't exist
    if not os.path.exists('data'):
        os.makedirs('data')
    
    # Download S&P 500 components list
    sp500 = pd.read_html('https://en.wikipedia.org/wiki/List_of_S%26P_500_companies')[0]
    symbols = sp500['Symbol'].tolist()
    
    # Set date range (5 years of data)
    end_date = datetime.now()
    start_date = end_date - timedelta(days=5*365)
    
    # Download data for each symbol
    for symbol in symbols[:5]:  # Starting with 5 stocks for testing
        print(f"Downloading data for {symbol}")
        df = download_stock_data(symbol, start_date, end_date)
        if df is not None:
            df.to_csv(f'data/{symbol}_data.csv')
            print(f"Successfully saved data for {symbol}")
            
            # Print sample of the data
            print(f"\nSample data for {symbol}:")
            print(df.head())
            print("\nShape:", df.shape)
            print("\nColumns:", df.columns.tolist())

if __name__ == "__main__":
    main()
